from http.cookies import SimpleCookie

from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@sync_to_async
def _get_user_for_token(token: str):
    jwt_auth = JWTAuthentication()
    try:
        validated = jwt_auth.get_validated_token(token)
        return jwt_auth.get_user(validated)
    except (AuthenticationFailed, InvalidToken, TokenError):
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        cookie_header = next(
            (value.decode('latin1') for key, value in scope.get('headers', []) if key == b'cookie'),
            '',
        )
        cookies = SimpleCookie(cookie_header)
        morsel = cookies.get(settings.JWT_ACCESS_COOKIE_NAME)
        token = morsel.value if morsel else None
        scope['user'] = await _get_user_for_token(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
