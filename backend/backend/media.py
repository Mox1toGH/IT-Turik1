from typing import Any, Optional

from django.conf import settings


def absolute_media_url(value: Any, context: Any = None) -> Optional[str]:
    """Return a browser-accessible URL for a media file or stored URL."""
    if not value:
        return None

    url = getattr(value, 'url', value)
    if not url:
        return None

    url = str(url)
    if url.startswith(('http://', 'https://', 'data:')):
        return url

    request = (context or {}).get('request')
    if request:
        return request.build_absolute_uri(url)

    return f"{settings.BACKEND_URL}/{url.lstrip('/')}"
