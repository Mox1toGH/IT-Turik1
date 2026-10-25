"""Optional process-RSS benchmark for the image upload pipeline.

Run from the repository root with:
    python -m backend.backend.benchmarks.image_upload_memory --workers 4

The worker reports its increase in peak RSS while decoding and re-encoding a
12-megapixel EXIF-oriented JPEG. This uses platform process counters rather
than tracemalloc, which cannot see Pillow's native pixel buffers.
"""

from __future__ import annotations

import argparse
import ctypes
import multiprocessing
import os
import sys
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

try:
    import resource
except ImportError:  # Windows reports peak working set through psapi instead.
    resource = None

from backend.backend.uploads import MAX_UPLOAD_BYTES, validate_and_clean_image


def peak_rss_bytes() -> int:
    if os.name == 'nt':
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ('cb', ctypes.c_ulong),
                ('PageFaultCount', ctypes.c_ulong),
                ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t),
                ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        ok = psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        )
        if not ok:
            raise OSError('GetProcessMemoryInfo failed')
        return counters.PeakWorkingSetSize

    if resource is None:
        raise RuntimeError('No process peak-RSS API is available on this platform.')
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == 'darwin' else peak * 1024)


def make_fixture() -> bytes:
    image = Image.new('RGB', (4000, 3000), (60, 100, 140))
    exif = Image.Exif()
    exif[274] = 6  # Include an orientation transform in the measured path.
    output = BytesIO()
    image.save(output, format='JPEG', quality=88, exif=exif)
    image.close()
    return output.getvalue()


def measure_upload(image_bytes: bytes) -> tuple[int, str | None]:
    upload = ContentFile(image_bytes, name='benchmark.jpg')
    baseline = peak_rss_bytes()
    cleaned, error = validate_and_clean_image(upload, max_size_bytes=MAX_UPLOAD_BYTES)
    peak = peak_rss_bytes()
    if cleaned is not None:
        cleaned.close()
    return max(0, peak - baseline), error


def process_upload(image_bytes: bytes, barrier, results) -> None:
    barrier.wait()
    delta, error = measure_upload(image_bytes)
    results.put((delta, error))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be at least 1')

    image_bytes = make_fixture()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise RuntimeError('Benchmark fixture exceeds the upload limit')

    context = multiprocessing.get_context('spawn')
    barrier = context.Barrier(args.workers)
    results = context.Queue()
    workers = [
        context.Process(target=process_upload, args=(image_bytes, barrier, results))
        for _ in range(args.workers)
    ]
    for worker in workers:
        worker.start()
    measurements = [results.get() for _ in workers]
    for worker in workers:
        worker.join()
        if worker.exitcode:
            raise RuntimeError(f'Benchmark worker exited with code {worker.exitcode}')

    for index, (delta, error) in enumerate(measurements, start=1):
        if error:
            raise RuntimeError(f'Worker {index} rejected fixture: {error}')
        print(f'worker {index}: peak RSS increase {delta / (1024 * 1024):.1f} MiB')
    print(f'workers: {args.workers}; fixture: {len(image_bytes) / 1024:.1f} KiB')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
