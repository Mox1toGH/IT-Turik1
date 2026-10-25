from ninja.security import HttpBearer
from django.conf import settings
from backend.auth_cookies import require_csrf
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

class JWTAuth(HttpBearer):
    """Required auth — raises 401 if token missing/invalid."""

    def __call__(self, request):
        cookie_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE_NAME)
        if cookie_token:
            require_csrf(request)
            return self.authenticate(request, cookie_token)
        return super().__call__(request)

    def authenticate(self, request, token):
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
        except (AuthenticationFailed, InvalidToken, TokenError):
            return None
        # TODO: remove request.auth, use user instead
        request.auth = user
        request.user = user
        return user

def authenticate(client, user):
    token = str(RefreshToken.for_user(user).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
