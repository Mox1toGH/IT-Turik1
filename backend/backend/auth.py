from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

class JWTAuth(HttpBearer):
    """Required auth — raises 401 if token missing/invalid."""

    def authenticate(self, request, token):
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
        except (InvalidToken, TokenError):
            return None
        request.auth = user  # доступно як request.auth у view-функції
        request.user = user
        return user


class OptionalJWTAuth(HttpBearer):
    """Optional auth — no token is fine, sets request.auth = None."""

    def authenticate(self, request, token):
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            request.auth = user
            request.user = user
            return user
        except (InvalidToken, TokenError):
            request.auth = None
            return 'anonymous'  # non-None означає "пропустити", але без юзера

def authenticate(client, user):
    token = str(RefreshToken.for_user(user).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")