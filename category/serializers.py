from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "user", "is_default")
        extra_kwargs = {
            "user": {
                "write_only": True
            },  # Prevent user from being visible in responses
            "is_default": {"read_only": True},  # Prevent non-admin users from modifying
        }

    def validate_name(self, value):
        user = self.context["request"].user

        # Check if a category with the same name exists for the user
        if Category.objects.filter(
            name__iexact=value, user=user, is_deleted=False
        ).exists():
            raise serializers.ValidationError(
                "A category with this name already exists for this user. Names are case-insensitive."
            )
        return value

    def create(self, validated_data):
        # Enforce the authenticated user as the owner of the category
        validated_data["user"] = self.context["request"].user

        # Restrict non-admin users from creating default categories
        if not self.context["request"].user.is_staff:
            validated_data["is_default"] = False

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent modification of the `user` field
        if "user" in validated_data:
            validated_data.pop("user")

        # Prevent non-admin users from modifying the `is_default` field
        if not self.context["request"].user.is_staff and "is_default" in validated_data:
            validated_data.pop("is_default")

        return super().update(instance, validated_data)
