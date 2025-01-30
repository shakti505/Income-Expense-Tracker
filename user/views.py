# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework import status
# from rest_framework.exceptions import NotFound
# from rest_framework.response import Response
# from utils.permissions import IsStaffUser, IsStaffOrOwner
# from utils.responses import success_response, validation_error_response, success_single_response

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


# class BaseUserView:
#     """
#     Base class for common user-related view operations
#     """

#     def get_user_or_404(self, id):
#         """
#         Retrieve user by ID or raise NotFound exception
#         """
#         try:
#             return CustomUser.objects.get(id=id)
#         except CustomUser.DoesNotExist:
#             raise NotFound(f"No user found with ID: {id}")


# class UserCreateView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         tokens = TokenHandler.generate_tokens_for_user(user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data["user"]

#         tokens = TokenHandler.generate_tokens_for_user(user)
#         return success_response(tokens)


# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         TokenHandler.invalidate_user_session(request.user, request.auth)
#         return success_response(
#             "Logged out successfully", status_code=status.HTTP_204_NO_CONTENT
#         )


# class UserListView(APIView):
#     permission_classes = [IsStaffUser]

#     def get(self, request):
#         users = CustomUser.objects.filter()
#         serializer = UserSerializer(users, many=True)
#         print(serializer.data)
#         return success_response(serializer.data)


# class UserProfileView(BaseUserView, TokenAuthorizationMixin, APIView):
#     permission_classes = [IsStaffOrOwner]

#     def get(self, request, id):
#         user = self.get_user_or_404(id)
#         self.check_object_permissions(request, user)
#         serializer = UserSerializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def patch(self, request, id):
#         user = self.get_user_or_404(id)
#         self.check_object_permissions(request, user)
#         serializer = UpdateUserSerializer(
#             instance=user, data=request.data, context={"request": request}, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def delete(self, request, id):
#         user = self.get_user_or_404(id)
#         self.check_object_permissions(request, user)

#         serializer = DeleteUserSerializer(
#             data=request.data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.delete_user()
#         return success_response(
#             "User account deleted", status_code=status.HTTP_204_NO_CONTENT
#         )


# class UpdatePasswordView(BaseUserView, APIView):
#     permission_classes = [IsStaffOrOwner]

#     def patch(self, request, id):
#         user = self.get_user_or_404(id)
#         self.check_object_permissions(request, user)
#         serializer = UpdatePasswordSerializer(
#             data=request.data, context={"request": request, "user": user}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.update_password()
#         return success_response("Password updated successfully")
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