"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django_asgi_app = get_asgi_application()

from notifications.routing import websocket_urlpatterns as notification_ws_urlpatterns  # noqa: E402
from evaluation.routing import websocket_urlpatterns as leaderboard_ws_urlpatterns  # noqa: E402
from notifications.ws_auth import JwtAuthMiddlewareStack  # noqa: E402

websocket_urlpatterns = [
    *notification_ws_urlpatterns,
    *leaderboard_ws_urlpatterns,
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        JwtAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
