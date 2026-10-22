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
        # TODO: remove request.auth, use user instead
        request.auth = user
        request.user = user
        return user

def authenticate(client, user):
    token = str(RefreshToken.for_user(user).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")