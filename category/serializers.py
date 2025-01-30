from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Category
from user.models import CustomUser


class CategorySerializer(serializers.ModelSerializer):
    # user = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Category
        fields = ["id", "name", "user", "is_default", "is_deleted"]
        read_only_fields = ["id", "is_default", "is_deleted"]

    def __init__(self, *args, **kwargs):
        # Get the request object from the context
        request = kwargs.get("context", {}).get("request", None)

        # If there's no request, proceed as usual
        if request:
            # Check HTTP method
            if request.method == "PATCH":
                # Custom logic for POST requests
                self.fields["user"].read_only = True

        # Ensure that parent initialization is called
        super().__init__(*args, **kwargs)

    def validate_user(self, user):
        """Validate that the user field is valid and can only be set by staff users during creation."""
        request = self.context.get("request")

        if not request.user.is_staff:
            raise serializers.ValidationError(
                "Only staff users can set the user field."
            )
        if not user:
            raise serializers.ValidationError("The user field cannot be blank.")
        if not user.is_active:
            raise serializers.ValidationError("The specified user does not exists.")
        return user

    def _validate_name(self, value, user):
        """Validate that the category name is unique for the determined user."""
        request = self.context.get("request")

        # Check if a category with the same name exists for the determined user
        if (
            Category.objects.filter(
                name__iexact=value, user=user, is_deleted=False
            ).exists()
            | Category.objects.filter(
                name__iexact=value, is_deleted=False, is_default=True
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
                data["name"] = self._validate_name(data["name"], user)

            data["user"] = user
            data["is_default"] = user.is_staff

        # For updates
        else:
            # Prevent staff users from updating the user field
            if "name" in data:
                data["name"] = self._validate_name(data["name"], self.instance.user)

        return data

    def create(self, validated_data):
        """Ensure the user and is_default fields are always set correctly before creating the category."""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Ensure the user field is not updated and other fields are updated correctly."""
        return super().update(instance, validated_data)
