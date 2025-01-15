import logging
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    PermissionDenied,
)
from .models import CustomUser, ActiveTokens
from category.models import Category
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# Set up logging
logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes user data for registration and viewing.
    """

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "password",
            "name",
            "created_at",
            "updated_at",
            "is_staff",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "is_staff": {"read_only": "True"},
        }

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        """

        user = CustomUser.objects.create_user(**validated_data)
        logger.info(f"User {user.username} created successfully.")
        return user


class LoginSerializer(serializers.Serializer):
    """
    Validates login credentials and returns the authenticated user.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the provided username and password against the database.
        """
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        logger.info(f"User {user.username} logged in successfully.")
        return {"user": user}


class DeleteUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.is_active:
            raise ValidationError("User is already deleted.")
        if not user.check_password(data["password"]):
            raise ValidationError("Wrong password.")
        return data

    def delete_user(self):
        user = self.context["request"].user
        if user.is_staff:
            # Remove user from categories they own or are associated with
            Category.objects.filter(user=user).update(user=None)
        TokenHandeling.invalidate_user_tokens(user)
        TokenHandeling.blacklist_refresh_token(self.validated_data["refresh_token"])
        user.is_active = False
        user.save()
        logger.info(f"User {user.username} soft-deleted successfully.")


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user details.
    """

    class Meta:
        model = CustomUser
        fields = ("username", "email", "name")

    def validate(self, attrs):
        if "password" in attrs:
            raise ValidationError("Do not include password in this field.")
        return attrs


class UpdatePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["password"]):
            raise ValidationError("Wrong password.")
        if data["password"] == data["new_password"]:
            raise ValidationError(
                "New password cannot be the same as the old password."
            )
        return data

    def update_password(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        TokenHandeling.invalidate_user_tokens(user)
        logger.info(f"User {user.username} updated their password successfully.")


class TokenHandeling:
    """
    TokenHandeling class for handling token-related operations.
    """

    @staticmethod
    def invalidate_user_tokens(user):
        """
        Invalidate all active tokens for a given user.
        """
        ActiveTokens.objects.filter(user=user).delete()
        logger.info(f"All tokens for user {user.username} invalidated.")

    @staticmethod
    def invalidate_last_active_token(access_token):
        ActiveTokens.objects.filter(token=access_token).delete()
        logger.info(f"Token {access_token} invalidated.")

    @staticmethod
    def blacklist_refresh_token(refresh_token):
        """Blacklist a given refresh token."""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"Refresh token {refresh_token} blacklisted.")
        except Exception as e:
            logger.error(f"Error blacklisting refresh token {refresh_token}: {str(e)}")
            raise Exception(f"Error blacklisting refresh token: {str(e)}")
