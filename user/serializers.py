from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import User
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes user data for registration and viewing.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "created_at",
            "is_staff",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "is_staff": {"write_only": True},
        }

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        """
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Hash the password before saving
        user.save()
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

        if user.is_deleted:
            raise PermissionDenied("Account is inactive")

        return {"user": user}
