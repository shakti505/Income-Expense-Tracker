import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ActiveTokens
from django.conf import settings
from rest_framework.exceptions import APIException


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        print("-------Custome Auth Method-------")
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            active_token = ActiveTokens.objects.filter(token=token).first()

            if not active_token:
                raise AuthenticationFailed("Token is invalid or has been logged out")

            user = active_token.user

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except Exception as e:
            raise UnauthorizedException(str(e))

        return (
            user,
            None,
        )


class UnauthorizedException(APIException):
    status_code = 401
    default_detail = "Unauthorized"
    default_code = "unauthorized"
