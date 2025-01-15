from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import ActiveTokens, CustomUser
from category.models import Category
from .serializers import (
    UserSerializer,
    LoginSerializer,
    UpdatePasswordSerializer,
    DeleteUserSerializer,
    UpdateUserSerializer,
    TokenHandeling,
)


class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "User created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# View to retrieve all users
class GetAllUsersView(APIView):
    """
    API view to retrieve all users. Only accessible by staff users.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Retrieve all users.
        """
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(
            {
                "message": "Users retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# View to retrieve, update, or delete a single user by ID
class GetUpdateDeleteSingleUserView(APIView):
    """
    API view to retrieve, update, or delete a single user by ID.
    """

    def get_user_object(self, id, requesting_user):
        """
        Helper function to get the user object and ensure access control.
        """
        user = get_object_or_404(CustomUser, id=id)
        # Only staff users or the user themselves can access this endpoint
        if not requesting_user.is_staff and requesting_user != user:
            raise PermissionDenied(
                "You do not have permission to access this resource."
            )
        return user

    def get(self, request, id):
        """
        Retrieve user details by ID.
        """
        user = self.get_user_object(id, request.user)
        serializer = UserSerializer(user)
        return Response(
            {
                "message": "User retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id):
        """
        Soft delete a user by ID.
        """
        user = self.get_user_object(id, request.user)

        serializer = DeleteUserSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete_user()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id):
        """
        Update user details by ID.
        """
        user = self.get_user_object(id, request.user)

        serializer = UpdateUserSerializer(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "User details updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpdatePasswordUserView(APIView):

    def patch(self, request, id):
        """
        Update password for a user by ID. Only staff can update others' passwords.
        """
        if not request.user.is_staff and request.user.id != id:
            raise PermissionDenied(
                "You do not have permission to change this user's password."
            )

        user = get_object_or_404(CustomUser, id=id)

        serializer = UpdatePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.update_password()

        return Response(
            {
                "message": "Password updated successfully.",
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Generate Tokens
        access_token = str(AccessToken.for_user(user))
        refresh_token = str(RefreshToken.for_user(user))
        ActiveTokens.objects.create(user=user, token=access_token)
        return Response(
            {
                "message": f"Login successful for {user.username}.",
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        access_token = request.headers.get("Authorization", "").split(" ")[1]
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {
                    "message": "Provide refresh token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        TokenHandeling.invalidate_last_active_token(access_token)
        TokenHandeling.blacklist_refresh_token(refresh_token)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
