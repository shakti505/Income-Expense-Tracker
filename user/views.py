# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework import status
# from rest_framework.response import Response
# from .permissions import IsStaffUser, IsStaffOrOwner
# from utils.responses import (
#     success_response,
#     validation_error_response,
#     success_single_response,
#     not_found_error_response,
# )
# from uuid import UUID
# from utils.token import TokenHandler
# from .models import CustomUser
# from .serializers import (
#     UserSerializer,
#     LoginSerializer,
#     UpdatePasswordSerializer,
#     DeleteUserSerializer,
#     UpdateUserSerializer,
# )
# from .authentication import TokenAuthorizationMixin
# from .tasks import send_email_task as send_mail
# from django.utils.http import urlsafe_base64_encode
# from django.contrib.auth.tokens import default_token_generator
# from .serializers import PasswordResetRequestSerializer
# from django.utils.http import urlsafe_base64_decode


# class BaseUserView:
#     """
#     Base class for common user-related view operations
#     """

#     def get_user_or_404(self, id):
#         """
#         Retrieve user by ID or raise NotFound exception
#         """
#         try:
#             user = CustomUser.objects.get(id=id)
#             return user
#         except CustomUser.DoesNotExist:
#             return not_found_error_response(f"No user found with ID: {id}")


# class UserCreateView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if not serializer.is_valid():
#             return validation_error_response(serializer.errors)
#         user = serializer.save()
#         tokens = TokenHandler.generate_tokens_for_user(user)
#         response_data = {"user": serializer.data, "tokens": tokens}
#         return success_response(response_data, status_code=status.HTTP_201_CREATED)


# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if not serializer.is_valid():
#             return validation_error_response(serializer.errors)
#         user = serializer.validated_data["user"]
#         tokens = TokenHandler.generate_tokens_for_user(user)
#         response_data = {"user": UserSerializer(user).data, "tokens": tokens}
#         return success_response(response_data)


# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         TokenHandler.invalidate_user_session(request.user, request.auth)
#         return success_response(
#             {"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
#         )


# class UserListView(APIView):
#     permission_classes = [IsStaffUser]

#     def get(self, request):
#         users = CustomUser.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return success_response(serializer.data)


# class UserProfileView(BaseUserView, TokenAuthorizationMixin, APIView):
#     permission_classes = [IsStaffOrOwner]

#     def get(self, request, id):
#         user = self.get_user_or_404(id)
#         self.check_object_permissions(request, user)
#         serializer = UserSerializer(user)
#         return success_single_response(serializer.data)

#     def patch(self, request, id):
#         user = self.get_user_or_404(id)
#         self.check_object_permissions(request, user)
#         serializer = UpdateUserSerializer(
#             instance=user, data=request.data, context={"request": request}, partial=True
#         )
#         if not serializer.is_valid():
#             return validation_error_response(serializer.errors)
#         serializer.save()
#         return success_single_response(serializer.data)

#     def delete(self, request, id):
#         user = self.get_user_or_404(id)
#         test = self.check_object_permissions(request, user)
#         target_user = CustomUser.objects.get(id=id)
#         serializer = DeleteUserSerializer(
#             data=request.data, context={"request": request, "user": target_user}
#         )
#         if not serializer.is_valid():
#             return validation_error_response(serializer.errors)
#         serializer.delete_user()
#         return success_response(
#             {"message": "User account deleted"}, status_code=status.HTTP_200_OK
#         )


# class UpdatePasswordView(BaseUserView, APIView):
#     permission_classes = [IsStaffOrOwner]

#     def patch(self, request, id):
#         user = self.get_user_or_404(id)
#         if isinstance(user, Response):
#             return user
#         self.check_object_permissions(request, user)
#         serializer = UpdatePasswordSerializer(
#             data=request.data, context={"request": request, "user": user}
#         )
#         if not serializer.is_valid():
#             return validation_error_response(serializer.errors)
#         serializer.update_password()
#         return success_response({"message": "Password updated successfully"})


# class PasswordResetRequestView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         # Use your custom serializer
#         serializer = PasswordResetRequestSerializer(data=request.data)

#         if serializer.is_valid():
#             email = serializer.validated_data["email"]
#             try:
#                 user = CustomUser.objects.get(email=email)
#                 print(user)
#                 print(email)
#             except CustomUser.DoesNotExist:
#                 return not_found_error_response(
#                     detail="User with this email not found."
#                 )

#             # Generate token
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(
#                 str(user.pk).encode()
#             )  # Use UUID bytes for encoding

#             # Generate reset URL
#             reset_link = (
#                 f"http://localhost:8000/api/auth/password-reset/confirm/{uid}/{token}/"
#             )
#             print("EHllo")
#             print(reset_link)
#             # Send email
#             send_mail.delay(
#                 [email],
#                 reset_link,
#             )
#             return success_response(data={"message": "Password reset email sent."})

#         return validation_error_response(serializer.errors)


# class PasswordResetConfirmView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, uidb64, token):
#         try:
#             # Decode UID
#             uid = urlsafe_base64_decode(uidb64).decode()

#             # Ensure the UID is a valid UUID
#             uid = UUID(uid)  # This will raise a ValueError if the UID is invalid

#             # Fetch the user using the decoded UID
#             user = CustomUser.objects.get(id=uid)
#         except (ValueError, CustomUser.DoesNotExist, TypeError):
#             return not_found_error_response(detail="Invalid user or token.")

#         # Check the token
#         if default_token_generator.check_token(user, token):
#             new_password = request.data.get("password")
#             print(new_password)
#             if new_password:
#                 user.set_password(new_password)
#                 user.save()
#                 return success_response(
#                     data={"message": "Password has been reset successfully."}
#                 )
#             return validation_error_response(errors={"detail": "Password is required."})

#         return validation_error_response(errors={"detail": "Invalid or expired token."})

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsStaffUser, IsStaffOrOwner
from utils.responses import (
    success_response,
    validation_error_response,
    success_single_response,
    not_found_error_response,
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
    PasswordResetRequestSerializer,
)
from .authentication import TokenAuthorizationMixin
from .tasks import send_email_task as send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.exceptions import NotFound


class BaseUserView:
    """
    Base class for common user-related view operations.
    """

    def get_user_or_404(self, id):
        """
        Retrieve a user by ID or return a 404 response if the user does not exist.

        Args:
            id (UUID): The ID of the user to retrieve.

        Returns:
            CustomUser: The user object if found.
            Response: A 404 response if the user is not found.
        """
        try:
            return CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            raise NotFound(f"No user found with ID: {id}")


class UserCreateView(APIView):
    """
    View for creating a new user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user.

        Args:
            request (Request): The request object containing user data.

        Returns:
            Response: A success response with the created user data and tokens,
                     or an error response if validation fails or an exception occurs.
        """
        try:
            serializer = UserSerializer(data=request.data)
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            user = serializer.save()
            tokens = TokenHandler.generate_tokens_for_user(user)
            response_data = {"user": serializer.data, "tokens": tokens}
            return success_response(response_data, status_code=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    """
    View for user login.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate a user and generate tokens.

        Args:
            request (Request): The request object containing login credentials.

        Returns:
            Response: A success response with user data and tokens,
                     or an error response if validation fails or an exception occurs.
        """
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            user = serializer.validated_data["user"]
            tokens = TokenHandler.generate_tokens_for_user(user)
            response_data = {"user": UserSerializer(user).data, "tokens": tokens}
            return success_response(response_data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """
    View for user logout.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Invalidate the user's session.

        Args:
            request (Request): The request object containing the authenticated user.

        Returns:
            Response: A success response indicating the user has been logged out,
                     or an error response if an exception occurs.
        """
        try:
            TokenHandler.invalidate_user_session(request.user, request.auth)
            return success_response(
                {"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserListView(APIView):
    """
    View for listing all users (accessible only by staff users).
    """

    permission_classes = [IsStaffUser]

    def get(self, request):
        """
        Retrieve a list of all users.

        Args:
            request (Request): The request object.

        Returns:
            Response: A success response with the list of users,
                     or an error response if an exception occurs.
        """
        try:
            users = CustomUser.objects.all()
            serializer = UserSerializer(users, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(BaseUserView, TokenAuthorizationMixin, APIView):
    """
    View for retrieving, updating, or deleting a user's profile.
    """

    permission_classes = [IsStaffOrOwner]

    def get(self, request, id):
        """
        Retrieve a user's profile by ID.

        Args:
            request (Request): The request object.
            id (UUID): The ID of the user to retrieve.

        Returns:
            Response: A success response with the user's profile data,
                     or an error response if the user is not found or an exception occurs.
        """
        try:
            user = self.get_user_or_404(id)
            self.check_object_permissions(request, user)
            serializer = UserSerializer(user)
            return success_single_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, id):
        """
        Update a user's profile by ID.

        Args:
            request (Request): The request object containing updated data.
            id (UUID): The ID of the user to update.

        Returns:
            Response: A success response with the updated user data,
                     or an error response if validation fails or an exception occurs.
        """
        try:
            user = self.get_user_or_404(id)
            self.check_object_permissions(request, user)
            serializer = UpdateUserSerializer(
                instance=user,
                data=request.data,
                context={"request": request},
                partial=True,
            )
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            serializer.save()
            return success_single_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, id):
        """
        Delete a user's account by ID.

        Args:
            request (Request): The request object.
            id (UUID): The ID of the user to delete.

        Returns:
            Response: A success response indicating the user has been deleted,
                     or an error response if validation fails or an exception occurs.
        """
        try:
            user = self.get_user_or_404(id)
            self.check_object_permissions(request, user)
            target_user = CustomUser.objects.get(id=id)
            print(request.data)
            serializer = DeleteUserSerializer(
                data=request.data, context={"request": request, "user": target_user}
            )
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            serializer.delete_user()
            return success_response(
                {"message": "User account deleted"}, status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdatePasswordView(BaseUserView, APIView):
    """
    View for updating a user's password.
    """

    permission_classes = [IsStaffOrOwner]

    def patch(self, request, id):
        """
        Update a user's password by ID.

        Args:
            request (Request): The request object containing the new password.
            id (UUID): The ID of the user whose password will be updated.

        Returns:
            Response: A success response indicating the password has been updated,
                     or an error response if validation fails or an exception occurs.
        """
        try:
            user = self.get_user_or_404(id)
            self.check_object_permissions(request, user)
            print(request.data["current_password"])
            serializer = UpdatePasswordSerializer(
                data=request.data, context={"request": request, "user": user}
            )
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            serializer.update_password()
            return success_response({"message": "Password updated successfully"})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetRequestView(APIView):
    """
    View for requesting a password reset.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle a password reset request.

        Args:
            request (Request): The request object containing the user's email.

        Returns:
            Response: A success response indicating the reset email has been sent,
                     or an error response if the user is not found or an exception occurs.
        """
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                try:
                    user = CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
                    return not_found_error_response(
                        detail="User with this email not found."
                    )

                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(str(user.pk).encode())
                reset_link = f"http://localhost:8000/api/auth/password-reset/confirm/{uid}/{token}/"
                send_mail.delay([email], reset_link)
                return success_response(data={"message": "Password reset email sent."})
            return validation_error_response(serializer.errors)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetConfirmView(APIView):
    """
    View for confirming a password reset.
    """

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """
        Confirm a password reset and update the user's password.

        Args:
            request (Request): The request object containing the new password.
            uidb64 (str): The base64-encoded user ID.
            token (str): The password reset token.

        Returns:
            Response: A success response indicating the password has been reset,
                     or an error response if the token is invalid or an exception occurs.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            uid = UUID(uid)
            user = CustomUser.objects.get(id=uid)
        except (ValueError, CustomUser.DoesNotExist, TypeError):
            return not_found_error_response(detail="Invalid user or token.")

        try:
            if default_token_generator.check_token(user, token):
                new_password = request.data.get("password")
                if new_password:
                    user.set_password(new_password)
                    user.save()
                    return success_response(
                        data={"message": "Password has been reset successfully."}
                    )
                return validation_error_response(
                    errors={"detail": "Password is required."}
                )
            return validation_error_response(
                errors={"detail": "Invalid or expired token."}
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
