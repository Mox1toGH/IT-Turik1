import secrets
from hmac import compare_digest

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from ninja.errors import HttpError


SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS', 'TRACE'}


def _cookie_options(*, path='/'):
    return {
        'path': path,
        'secure': settings.JWT_COOKIE_SECURE,
        'samesite': settings.JWT_COOKIE_SAMESITE,
    }


def _csrf_token(request):
    return request.COOKIES.get(settings.JWT_CSRF_COOKIE_NAME) or secrets.token_urlsafe(32)


def csrf_response(request):
    token = _csrf_token(request)
    response = JsonResponse({'csrf_token': token})
    response.set_cookie(
        settings.JWT_CSRF_COOKIE_NAME,
        token,
        httponly=False,
        max_age=7 * 24 * 60 * 60,
        **_cookie_options(),
    )
    return response


def auth_response(request, data, *, access_token, refresh_token=None, status=200):
    body = {**data, 'csrf_token': _csrf_token(request)}
    response = JsonResponse(body, status=status)
    response.set_cookie(
        settings.JWT_ACCESS_COOKIE_NAME,
        access_token,
        httponly=True,
        max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        **_cookie_options(),
    )
    if refresh_token:
        response.set_cookie(
            settings.JWT_REFRESH_COOKIE_NAME,
            refresh_token,
            httponly=True,
            max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
            **_cookie_options(path='/api/accounts/token/refresh'),
        )
    return response


def require_csrf(request):
    if request.method in SAFE_METHODS:
        return

    origin = request.headers.get('Origin')
    trusted_origins = set(getattr(settings, 'CORS_ALLOWED_ORIGINS', ()))
    if origin and origin not in trusted_origins:
        raise HttpError(403, 'Untrusted request origin.')

    has_cookie_auth = (
        settings.JWT_ACCESS_COOKIE_NAME in request.COOKIES
        or settings.JWT_REFRESH_COOKIE_NAME in request.COOKIES
    )
    if not (origin or has_cookie_auth):
        return

    cookie_token = request.COOKIES.get(settings.JWT_CSRF_COOKIE_NAME, '')
    header_token = request.headers.get('X-CSRFToken', '')
    if not cookie_token or not header_token or not compare_digest(cookie_token, header_token):
        raise HttpError(403, 'CSRF verification failed.')


def clear_auth_cookies(response: HttpResponse):
    for cookie_name, path in (
        (settings.JWT_ACCESS_COOKIE_NAME, '/'),
        (settings.JWT_REFRESH_COOKIE_NAME, '/api/accounts/token/refresh'),
        (settings.JWT_CSRF_COOKIE_NAME, '/'),
    ):
        response.delete_cookie(
            cookie_name,
            path=path,
            samesite=settings.JWT_COOKIE_SAMESITE,
            secure=settings.JWT_COOKIE_SECURE,
        )
    return response
