
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from utils.permissions import IsStaffUser, IsStaffOrOwner
from utils.responses import (
    success_response,
    validation_error_response,
    success_single_response,
    not_found_error_response
)
from uuid import UUID
from utils.token import TokenHandler
from .models import CustomUser
from .serializers import (
    UserSerializer,
    LoginSerializer,
    UpdatePasswordSerializer,
    DeleteUserSerializer,
    UpdateUserSerializer,
)
from .authentication import TokenAuthorizationMixin
from .tasks import send_email_task as send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from .serializers import PasswordResetRequestSerializer
from django.utils.http import urlsafe_base64_decode



class BaseUserView:
    """
    Base class for common user-related view operations
    """

    def get_user_or_404(self, id):
        """
        Retrieve user by ID or raise NotFound exception
        """
        try:
            return CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return not_found_error_response(f"No user found with ID: {id}")


class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        user = serializer.save()
        tokens = TokenHandler.generate_tokens_for_user(user)
        response_data = {
            "user": serializer.data,
            "tokens": tokens
        }
        return success_response(response_data, status_code=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        user = serializer.validated_data["user"]
        tokens = TokenHandler.generate_tokens_for_user(user)
        response_data = {
            "user": UserSerializer(user).data,
            "tokens": tokens
        }
        return success_response(response_data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        TokenHandler.invalidate_user_session(request.user, request.auth)
        return success_response({"message": "Logged out successfully"}, status_code=status.HTTP_200_OK)


class UserListView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return success_response(serializer.data)


class UserProfileView(BaseUserView, TokenAuthorizationMixin, APIView):
    permission_classes = [IsStaffOrOwner]

    def get(self, request, id):
        user = self.get_user_or_404(id)
        if isinstance(user, Response):  # If not_found_error_response was returned
            return user
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user)
        return success_single_response(serializer.data)

    def patch(self, request, id):
        user = self.get_user_or_404(id)
        if isinstance(user, Response):
            return user
        self.check_object_permissions(request, user)
        serializer = UpdateUserSerializer(
            instance=user,
            data=request.data,
            context={"request": request},
            partial=True
        )
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        serializer.save()
        return success_single_response(serializer.data)

    def delete(self, request, id):
        user = self.get_user_or_404(id)
        if isinstance(user, Response):
            return user
        self.check_object_permissions(request, user)

        serializer = DeleteUserSerializer(
            data=request.data,
            context={"request": request}
        )
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        serializer.delete_user()
        return success_response(
            {"message": "User account deleted"},
            status_code=status.HTTP_200_OK
        )


class UpdatePasswordView(BaseUserView, APIView):
    permission_classes = [IsStaffOrOwner]

    def patch(self, request, id):
        user = self.get_user_or_404(id)
        if isinstance(user, Response):
            return user
        self.check_object_permissions(request, user)
        serializer = UpdatePasswordSerializer(
            data=request.data,
            context={"request": request, "user": user}
        )
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        serializer.update_password()
        return success_response({"message": "Password updated successfully"})
    



class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # Use your custom serializer
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return not_found_error_response(detail="User with this email not found.")
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode()) # Use UUID bytes for encoding

            # Generate reset URL
            reset_link = f'http://localhost:8000/api/auth/password-reset/confirm/{uid}/{token}/'

            # Send email
            send_mail.delay(
                [email],
                reset_link,)
            return success_response(data={'message': 'Password reset email sent.'})

        return validation_error_response(serializer.errors)



class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, uidb64, token):
        try:
            # Decode UID
            uid = urlsafe_base64_decode(uidb64).decode()

            # Ensure the UID is a valid UUID
            uid = UUID(uid)  # This will raise a ValueError if the UID is invalid

            # Fetch the user using the decoded UID
            user = CustomUser.objects.get(id=uid)
        except (ValueError, CustomUser.DoesNotExist, TypeError):
            return not_found_error_response(detail="Invalid user or token.")
        
        # Check the token
        if default_token_generator.check_token(user, token):
            new_password = request.data.get('password')
            print(new_password)
            if new_password:
                user.set_password(new_password)
                user.save()
                return success_response(data={'message': 'Password has been reset successfully.'})
            return validation_error_response(errors={"detail": "Password is required."})

        return validation_error_response(errors={"detail": "Invalid or expired token."})