from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from threading import Lock
import time

import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, PngImagePlugin, features

try:
    from backend.uploads import MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES, validate_and_clean_image
except ModuleNotFoundError:  # Also support pytest launched from the repository root.
    from backend.backend.uploads import MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES, validate_and_clean_image


def make_image_bytes(image_format: str, size=(32, 24), **save_options) -> bytes:
    image = Image.new('RGB', size, (24, 80, 140))
    result = BytesIO()
    image.save(result, format=image_format, **save_options)
    image.close()
    return result.getvalue()


@pytest.mark.parametrize('image_format', ['JPEG', 'PNG', 'WEBP'])
def test_accepts_supported_formats_and_returns_django_file(image_format):
    upload = ContentFile(make_image_bytes(image_format), name='user-supplied-name.bin')

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert error is None
    assert cleaned is not None
    assert isinstance(cleaned.name, str)
    assert cleaned.name.endswith(('.jpg', '.png', '.webp'))
    assert cleaned.file.tell() == 0
    with Image.open(cleaned) as image:
        image.verify()
    cleaned.close()


def test_rejects_empty_upload():
    upload = ContentFile(b'', name='empty.jpg')

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert cleaned is None
    assert error == 'The uploaded image is empty.'
    assert upload.tell() == 0


def test_rejects_oversized_upload_before_decoding():
    upload = ContentFile(b'x' * (MAX_UPLOAD_BYTES + 1), name='large.jpg')

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES * 2)

    assert cleaned is None
    assert error == 'Image must be no larger than 5 MB.'
    assert upload.tell() == 0


def test_rejects_corrupted_image_and_restores_pointer():
    upload = ContentFile(b'not an image', name='broken.png')
    upload.seek(4)

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert cleaned is None
    assert error == 'The uploaded file is not a valid supported image.'
    assert upload.tell() == 0
    assert upload.read() == b'not an image'


def test_rejects_content_that_spoofs_image_name_and_mime_type():
    upload = SimpleUploadedFile(
        'payload.jpg',
        b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
        content_type='image/jpeg',
    )

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert cleaned is None
    assert error == 'The uploaded file is not a valid supported image.'
    assert upload.tell() == 0


def test_rejects_image_over_pixel_limit_before_full_decode():
    # A highly compressible PNG stays small while exceeding the pixel limit.
    width = 4000
    height = MAX_IMAGE_PIXELS // width + 1
    upload = ContentFile(make_image_bytes('PNG', (width, height)), name='huge.png')
    assert upload.size <= MAX_UPLOAD_BYTES

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert cleaned is None
    assert error == 'Image dimensions must not exceed 12 million pixels.'
    assert upload.tell() == 0


def test_applies_exif_orientation_and_removes_exif_metadata():
    exif = Image.Exif()
    exif[274] = 6  # Rotate 90 degrees clockwise for display.
    exif[270] = 'private description'
    image = Image.new('RGB', (2, 3), (200, 20, 20))
    source = BytesIO()
    image.save(source, format='JPEG', exif=exif)
    image.close()
    source_bytes = source.getvalue()
    upload = ContentFile(source_bytes, name='photo.jpg')

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert error is None
    assert cleaned is not None
    with Image.open(cleaned) as result:
        assert result.size == (3, 2)
        assert not result.getexif()
    assert upload.read() == source_bytes
    assert upload.tell() == 0
    cleaned.close()


def test_removes_png_text_metadata():
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text('Comment', 'private description')
    upload = ContentFile(
        make_image_bytes('PNG', pnginfo=metadata),
        name='photo.png',
    )

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert error is None
    assert cleaned is not None
    with Image.open(cleaned) as result:
        assert 'Comment' not in result.info
    cleaned.close()


def test_rejects_animated_webp():
    if not features.check('webp'):
        pytest.skip('This Pillow build does not support WebP.')
    first = Image.new('RGB', (8, 8), 'red')
    second = Image.new('RGB', (8, 8), 'blue')
    source = BytesIO()
    try:
        first.save(source, format='WEBP', save_all=True, append_images=[second], duration=100)
    except (OSError, ValueError):
        pytest.skip('This Pillow build does not support animated WebP encoding.')
    first.close()
    second.close()
    upload = ContentFile(source.getvalue(), name='animated.webp')

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert cleaned is None
    assert error == 'Animated and multi-frame images are not supported.'
    assert upload.tell() == 0


def test_honors_smaller_caller_size_limit():
    upload = ContentFile(b'x' * (1024 * 1024 + 1), name='small-limit.png')

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=1024 * 1024)

    assert cleaned is None
    assert error == 'Image must be no larger than 1 MB.'


def test_original_upload_bytes_are_never_changed():
    original = make_image_bytes('PNG')
    upload = ContentFile(original, name='source.png')
    upload.seek(5)

    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)

    assert error is None
    assert cleaned is not None
    assert upload.tell() == 0
    assert upload.read() == original
    cleaned.close()


def test_parallel_calls_limit_full_decodes_to_one_per_process(monkeypatch):
    uploads_module = import_module(validate_and_clean_image.__module__)

    original_load = Image.Image.load
    lock = Lock()
    active_decodes = 0
    peak_decodes = 0

    def tracked_load(image, *args, **kwargs):
        nonlocal active_decodes, peak_decodes
        with lock:
            active_decodes += 1
            peak_decodes = max(peak_decodes, active_decodes)
        try:
            # Give competing threads a chance to reach load() simultaneously.
            time.sleep(0.02)
            return original_load(image, *args, **kwargs)
        finally:
            with lock:
                active_decodes -= 1

    monkeypatch.setattr(uploads_module.Image.Image, 'load', tracked_load)
    data = make_image_bytes('PNG', (300, 200))

    def validate_one(_):
        result, error = validate_and_clean_image(
            ContentFile(data, name='parallel.png'),
            max_size_bytes=MAX_UPLOAD_BYTES,
        )
        assert error is None
        assert result is not None
        result.close()

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(validate_one, range(4)))

    assert peak_decodes == 1
