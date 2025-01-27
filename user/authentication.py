import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from rest_framework import exceptions
from .models import ActiveTokens


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Custom token authentication method.

        Validates JWT token, checks token validity, and user status.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Check token in ActiveTokens
            active_token = ActiveTokens.objects.filter(
                token=token,
            ).first()
            if not active_token:
                raise AuthenticationFailed("Invalid or expired token")

            user = active_token.user
            if not user.is_active:
                raise AuthenticationFailed("User account is inactive")

            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except Exception as e:
            raise AuthenticationFailed(str(e))


class TokenAuthorizationMixin:
    """
    Mixin to provide additional token authorization methods.
    """

    def get_authorized_user(self, request, id):
        """
        Validate user authorization for specific operations.
        """
        if not request.user.is_staff and request.user.id != id:
            raise exceptions.PermissionDenied("Unauthorized access")
        return request.user
