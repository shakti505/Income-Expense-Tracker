import logging
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import CustomUser, ActiveTokens
from category.models import Category
from utils.token import TokenHandler
from django.contrib.auth.password_validation import validate_password

logger = logging.getLogger(__name__)


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = (
#             "id",
#             "username",
#             "email",
#             "password",
#             "name",
#             "created_at",
#             "updated_at",
#             "is_active",
#             "is_staff",
#         )
#         extra_kwargs = {
#             "password": {"write_only": True},
#             "id": {"read_only": True},
#             "created_at": {"read_only": True},
#             "updated_at": {"read_only": True},
#             "is_active": {"read_only": True},
#             "is_staff": {"read_only": True},
#         }

#     def validate_password(self, value):
#         validate_password(value)
#         return value

#     def create(self, validated_data):
#         user = CustomUser.objects.create_user(**validated_data)
#         logger.info(f"User {user.username} created successfully.")
#         return user


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data.get("username")
#         password = data.get("password")

#         user = authenticate(username=username, password=password)
#         if not user:
#             raise AuthenticationFailed("Invalid credentials")

#         if not user.is_active:
#             raise AuthenticationFailed("Account is inactive")

#         logger.info(f"User {user.username} logged in successfully.")
#         data["user"] = user
#         return data


# class UpdatePasswordSerializer(serializers.Serializer):
#     current_password = serializers.CharField(write_only=True, required=False)
#     new_password = serializers.CharField(write_only=True)
#     confirm_password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = self.context["user"]
#         request_user = self.context["request"].user

#         # If the request user is not staff, validate current password
#         if not request_user.is_staff:
#             if "current_password" not in data:
#                 raise ValidationError("Current password is required.")
#             if not user.check_password(data["current_password"]):
#                 raise ValidationError("Current password is incorrect.")

#         # Validate new passwords
#         if data["new_password"] != data["confirm_password"]:
#             raise ValidationError("New passwords do not match.")

#         validate_password(data["new_password"], user)

#         # Prevent reusing the current password
#         if user.check_password(data["new_password"]):
#             raise ValidationError(
#                 "New password cannot be the same as the current password."
#             )

#         return data

#     def update_password(self):
#         user = self.context["user"]
#         user.set_password(self.validated_data["new_password"])
#         user.save()

#         # Invalidate all other tokens except the current one
#         ActiveTokens.objects.filter(user=user).exclude(
#             token=self.context["request"].auth
#         ).delete()

#         logger.info(f"User {user.username} updated password successfully.")


# class DeleteUserSerializer(serializers.Serializer):
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = self.context["request"].user
#         print(user)
#         if not user.check_password(data["password"]):
#             raise ValidationError("Incorrect password")

#         return data

#     def delete_user(self):
#         user = self.context["request"].user

#         # Soft delete user
#         user.is_active = False
#         user.save()

#         # Optional: Update related records
#         if user.is_staff:
#             Category.objects.filter(user=user).update(user=None)

#         # Invalidate all tokens
#         ActiveTokens.objects.filter(user=user).delete()

#         logger.info(f"User {user.username} soft-deleted successfully.")


# class UpdateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ["username", "email", "name"]

#     def validate_username(self, value):
#         # Ensure username is unique, excluding current user
#         user = self.context["request"].user
#         if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
#             raise ValidationError("Username already exists")
#         return value

#     def validate_email(self, value):
#         # Ensure email is unique, excluding current user
#         user = self.context["request"].user
#         if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
#             raise ValidationError("Email already exists")
#         return value


# class PasswordResetRequestSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         try:
#             user = CustomUser.objects.get(email=value)
#         except CustomUser.DoesNotExist:
#             raise serializers.ValidationError("No user found with this email address.")
#         return value

import re
import logging
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import CustomUser, ActiveTokens
from category.models import Category
from utils.token import TokenHandler
from django.contrib.auth.password_validation import validate_password

logger = logging.getLogger(__name__)


class PasswordValidationMixin:
    def validate_password_strength(self, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError(
                "Password must contain at least one special character"
            )


# class BaseUserValidationMixin(PasswordValidationMixin):
#     def validate_unique_field(self, field_name, value, model_class):
#         user = self.context["request"].user
#         if (
#             model_class.objects.exclude(pk=user.pk)
#             .filter(**{field_name: value})
#             .exists()
#         ):
#             raise ValidationError(f"{field_name.title()} already exists")
#         return value

#     def validate_passwords_match(self, new_password, confirm_password):
#         if new_password != confirm_password:
#             raise ValidationError("New passwords do not match.")
#         self.validate_password_strength(new_password)

#     def validate_password_reuse(self, user, new_password):
#         if user.check_password(new_password):
#             raise ValidationError(
#                 "New password cannot be the same as the current password."
#             )

#     def validate_current_password(self, user, current_password):
#         logger.debug(f"Validating current password for user: {user.username}")
#         if not user.check_password(current_password):
#             logger.warning(
#                 f"Current password validation failed for user: {user.username}"
#             )
#             raise ValidationError("Current password is incorrect.")


class BaseUserValidationMixin(PasswordValidationMixin):
    def validate_unique_field(self, field_name, value, model_class):
        user = self.context["request"].user
        if (
            model_class.objects.exclude(pk=user.pk)
            .filter(**{field_name: value})
            .exists()
        ):
            raise ValidationError(f"{field_name.title()} already exists")
        return value

    def validate_passwords_match(self, new_password, confirm_password):
        if new_password != confirm_password:
            raise ValidationError("New passwords do not match.")
        self.validate_password_strength(new_password)

    def validate_password_reuse(self, user, new_password):
        if user.check_password(new_password):
            raise ValidationError(
                "New password cannot be the same as the current password."
            )

    def validate_current_password(self, current_password):
        """
        Validate the current password for a user.

        Args:
            current_password: The password to validate

        Raises:
            ValidationError: If the current password is incorrect
        """
        user = self.context["user"]
        logger.debug(f"Validating current password for user: {user.username}")
        if not current_password:
            raise ValidationError("Current password is required.")
        if not user.check_password(current_password):
            logger.warning(
                f"Current password validation failed for user: {user.username}"
            )
            raise ValidationError("Current password is incorrect.")


class UserSerializer(serializers.ModelSerializer, BaseUserValidationMixin):
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
        self.validate_password_strength(value)
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


class UpdatePasswordSerializer(BaseUserValidationMixin, serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, current_password):
        return current_password

    def validate(self, data):
        user = self.context["user"]
        request_user = self.context["request"].user
        # print(self.context)
        print(data.get("current_password"))
        # Staff validation
        if request_user.is_staff:
            if user.is_staff and user != request_user:
                raise ValidationError(
                    "Staff members cannot modify other staff members' passwords"
                )
        else:
            print(data["current_password"])
            if "current_password" not in data:
                raise ValidationError("Current password is required.")
            self.validate_current_password(data["current_password"])

        self.validate_passwords_match(data["new_password"], data["confirm_password"])
        validate_password(data["new_password"], user)
        self.validate_password_reuse(user, data["new_password"])

        return data

    def update_password(self):
        user = self.context["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()

        ActiveTokens.objects.filter(user=user).exclude(
            token=self.context["request"].auth
        ).delete()

        logger.info(f"User {user.username} updated password successfully.")


class DeleteUserSerializer(serializers.Serializer, BaseUserValidationMixin):
    current_password = serializers.CharField(write_only=True, required=False)

    def validate_current_password(self, current_password):
        return current_password

    def validate(self, data):
        user = self.context["request"].user
        target_user = self.context.get("user")
        print(data["current_password"])
        if user.is_staff:
            if target_user.is_staff:
                raise ValidationError(
                    "Staff members cannot delete other staff accounts"
                )
            return data

        if not data.get("current_password"):
            raise ValidationError("Password is required")
        return data

    def delete_user(self):
        user = self.context["user"]
        user.is_active = False
        user.save()

        if user.is_staff:
            Category.objects.filter(user=user).update(user=None)

        ActiveTokens.objects.filter(user=user).delete()
        logger.info(f"User {user.username} soft-deleted successfully.")


class UpdateUserSerializer(BaseUserValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "name"]

    def validate_username(self, value):
        return self.validate_unique_field("username", value, CustomUser)

    def validate_email(self, value):
        return self.validate_unique_field("email", value, CustomUser)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise ValidationError("No user found with this email address.")

        return value
