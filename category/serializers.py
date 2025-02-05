from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Category
from user.models import CustomUser


class CategorySerializer(serializers.ModelSerializer):
    # user = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Category
        fields = ["id", "name", "user", "is_predefined", "type"]
        read_only_fields = [
            "id",
            "is_predefined",
        ]

    def __init__(self, *args, **kwargs):
        # Get the request object from the context
        request = kwargs.get("context", {}).get("request")

        # If there's no request, proceed as usual
        if request:
            # Check HTTP method
            if request.method == "PATCH":
                self.fields["user"].read_only = True
                self.fields["type"].read_only = True

        # Ensure that parent initialization is called
        super().__init__(*args, **kwargs)

    def validate_user(self, user):
        """Custom validation for user: Ensure the user is active,
        normal users can only create categories for themselves,
        and staff cannot create categories for other staff."""
        request = self.context.get("request")

        # Ensure the user exists and is active
        if not user or not user.is_active:
            raise serializers.ValidationError(
                "The specified user is either invalid or inactive."
            )

        # Normal users can only create categories for themselves
        if not request.user.is_staff and user != request.user:
            raise PermissionDenied(
                "Normal users can only create categories for themselves."
            )

        # Staff users can create categories for themselves, but not for other staff users
        if request.user.is_staff:
            if user != request.user and user.is_staff:
                raise PermissionDenied(
                    "Staff users cannot create categories for other staff users."
                )

        return user

    def _validate_name(self, value, user, type):
        """Validate that the category name is unique for the determined user."""
        request = self.context.get("request")
        print(type)

        # Check if a category with the same name exists for the determined user
        if (
            Category.objects.filter(
                name__iexact=value, user=user, is_deleted=False, type=type
            ).exists()
            or Category.objects.filter(
                name__iexact=value, is_deleted=False, is_predefined=True, type=type
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    "name": f"A category with the name '{value}' already exists for the user or predifined."
                }
            )

        return value

    def validate(self, data):
        """Ensure the user field is handled correctly during creation and updates."""
        request = self.context.get("request")
        # For creation
        if self.instance is None:
            # If the user is not staff, force the user field to be the authenticated user
            user = data.get("user", request.user)
            if "name" in data:
                data["name"] = self._validate_name(data["name"], user, data.get("type"))

            data["user"] = user
            data["is_predefined"] = user.is_staff

        # For updates
        else:
            # Prevent staff users from updating the user field
            if "name" in data:
                data["name"] = self._validate_name(
                    data["name"], self.instance.user, self.instance.type
                )

        return data

    def create(self, validated_data):
        """Ensure the user and is_predefined fields are always set correctly before creating the category."""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Ensure the user field is not updated and other fields are updated correctly."""
        return super().update(instance, validated_data)
