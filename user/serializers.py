import logging
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import CustomUser, ActiveTokens
from category.models import Category
from utils.token import TokenHandler
from django.contrib.auth.password_validation import validate_password

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
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
            "is_active",
            "is_staff",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "is_active": {"read_only": True},
            "is_staff": {"read_only": True},
        }
        

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        logger.info(f"User {user.username} created successfully.")
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("Account is inactive")

        logger.info(f"User {user.username} logged in successfully.")
        data["user"] = user
        return data


class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["user"]
        request_user = self.context["request"].user

        # If the request user is not staff, validate current password
        if not request_user.is_staff:
            if "current_password" not in data:
                raise ValidationError("Current password is required.")
            if not user.check_password(data["current_password"]):
                raise ValidationError("Current password is incorrect.")

        # Validate new passwords
        if data["new_password"] != data["confirm_password"]:
            raise ValidationError("New passwords do not match.")

        validate_password(data["new_password"], user)

        # Prevent reusing the current password
        if user.check_password(data["new_password"]):
            raise ValidationError(
                "New password cannot be the same as the current password."
            )

        return data

    def update_password(self):
        user = self.context["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()

        # Invalidate all other tokens except the current one
        ActiveTokens.objects.filter(user=user).exclude(
            token=self.context["request"].auth
        ).delete()

        logger.info(f"User {user.username} updated password successfully.")


class DeleteUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user

        if not user.is_active:
            raise ValidationError("User account is already deleted")

        if not user.check_password(data["password"]):
            raise ValidationError("Incorrect password")

        return data

    def delete_user(self):
        user = self.context["request"].user

        # Soft delete user
        user.is_active = False
        user.save()

        # Optional: Update related records
        if user.is_staff:
            Category.objects.filter(user=user).update(user=None)

        # Invalidate all tokens
        ActiveTokens.objects.filter(user=user).delete()

        logger.info(f"User {user.username} soft-deleted successfully.")


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "name"]

    def validate_username(self, value):
        # Ensure username is unique, excluding current user
        user = self.context["request"].user
        if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        # Ensure email is unique, excluding current user
        user = self.context["request"].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise ValidationError("Email already exists")
        return value
