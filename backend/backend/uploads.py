from __future__ import annotations

from http.client import IncompleteRead
from threading import BoundedSemaphore
from tempfile import TemporaryFile
from typing import BinaryIO
from uuid import uuid4
import warnings
import struct
import zlib

from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError


MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000
SUPPORTED_IMAGE_FORMATS = {
    'JPEG': 'jpg',
    'PNG': 'png',
    'WEBP': 'webp',
}
_IMAGE_PROCESSING_SLOT = BoundedSemaphore(value=1)


class _OutputTooLarge(Exception):
    pass


class _BoundedWriter:
    """File-like adapter that prevents a re-encoded image exceeding its limit."""

    def __init__(self, file: BinaryIO, max_bytes: int):
        self.file = file
        self.max_bytes = max_bytes

    def write(self, data: bytes) -> int:
        if self.file.tell() + len(data) > self.max_bytes:
            raise _OutputTooLarge
        return self.file.write(data)

    def seek(self, *args):
        return self.file.seek(*args)

    def tell(self) -> int:
        return self.file.tell()

    def flush(self) -> None:
        self.file.flush()


def validate_and_clean_image(
    upload: UploadedFile,
    *,
    max_size_bytes: int,
) -> tuple[File | None, str | None]:
    """Validate and re-encode a single-frame JPEG, PNG, or WebP image.

    The encoded result is disk-backed so concurrent uploads do not each retain
    a second full encoded image in RAM. The caller owns and must close a
    successful returned file after saving it to storage.
    """
    size_limit = min(max_size_bytes, MAX_UPLOAD_BYTES)
    mebibyte = 1024 * 1024
    if size_limit % mebibyte == 0:
        size_limit_label = f'{size_limit // mebibyte} MB'
    else:
        size_limit_label = f'{size_limit} byte' if size_limit == 1 else f'{size_limit} bytes'
    size_error = f'Image must be no larger than {size_limit_label}.'
    output_file: BinaryIO | None = None
    transferred = False

    try:
        if upload.size <= 0:
            return None, 'The uploaded image is empty.'
        if size_limit <= 0 or upload.size > size_limit:
            return None, size_error

        with _IMAGE_PROCESSING_SLOT, warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            upload.seek(0)
            with Image.open(upload) as image:
                image_format = image.format
                if image_format not in SUPPORTED_IMAGE_FORMATS:
                    return None, 'Upload a JPEG, PNG, or WebP image.'
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    return None, 'Image dimensions must not exceed 12 million pixels.'
                if getattr(image, 'n_frames', 1) != 1:
                    return None, 'Animated and multi-frame images are not supported.'

                # verify() checks the encoded stream without retaining a decoded
                # bitmap. Reopening below is required before a full decode.
                image.verify()

            upload.seek(0)
            with Image.open(upload) as image:
                if image.format != image_format:
                    return None, 'The uploaded file is not a valid supported image.'

                # This also fully decodes the source. In-place mode avoids a
                # second full-size copy when no orientation transform is needed.
                ImageOps.exif_transpose(image, in_place=True)

                # Retain only PNG palette transparency, which affects rendered
                # pixels. Other source metadata is deliberately discarded.
                palette_transparency = (
                    image.info.get('transparency')
                    if image_format == 'PNG' and image.mode == 'P'
                    else None
                )
                image.info.clear()
                if palette_transparency is not None:
                    image.info['transparency'] = palette_transparency

                # Pillow's WebP encoder returns one encoded byte string before
                # writing it to a file object. Route WebP inputs through the
                # streaming JPEG/PNG encoders instead to keep output disk-backed.
                output_format = image_format
                if image_format == 'WEBP':
                    output_format = 'PNG' if 'A' in image.mode else 'JPEG'

                output_file = TemporaryFile(mode='w+b')
                bounded_output = _BoundedWriter(output_file, size_limit)
                save_options = {'quality': 90} if output_format == 'JPEG' else {}
                image.save(bounded_output, format=output_format, **save_options)

        output_file.seek(0)
        cleaned_file = File(
            output_file,
            name=f'{uuid4().hex}.{SUPPORTED_IMAGE_FORMATS[output_format]}',
        )
        transferred = True
        return cleaned_file, None
    except _OutputTooLarge:
        return None, size_error
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        EOFError,
        IncompleteRead,
        SyntaxError,
        ValueError,
        struct.error,
        zlib.error,
    ):
        return None, 'The uploaded file is not a valid supported image.'
    finally:
        try:
            upload.seek(0)
        finally:
            if output_file is not None and not transferred:
                output_file.close()
