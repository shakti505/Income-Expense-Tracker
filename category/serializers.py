from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "is_default", "user")
        extra_kwargs = {
            "is_default": {"read_only": True},
        }

    def validate_name(self, value):
        user = self.context["request"].user

        # Check if a category with the same name exists for the user (normal user check)
        if Category.objects.filter(
            name__iexact=value, user=user, is_deleted=False
        ).exists():
            raise serializers.ValidationError(
                "A category with this name already exists for this user. Names are case-insensitive."
            )

        # If the user is a normal user (not staff), check if the category exists as a default category
        if not user.is_staff:
            if Category.objects.filter(
                name__iexact=value, is_default=True, is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    "A default category with this name already exists. Normal users cannot create new categories with this name."
                )

        if user.is_staff:
            if Category.objects.filter(
                name__iexact=value, is_deleted=False, is_default=True
            ).exists():
                raise serializers.ValidationError(
                    "A default category with this name already exists. Staff members cannot create new categories with this name."
                )

        return value

    def create(self, validated_data):
        # Enforce the authenticated user as the owner of the category
        validated_data["user"] = self.context["request"].user

        # Restrict non-admin users from creating default categories
        if self.context["request"].user.is_staff:
            validated_data["is_default"] = True

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent modification of the `user` field
        if "user" in validated_data:
            validated_data.pop("user")
        # Prevent non-admin users from modifying the `is_default` field
        if not self.context["request"].user.is_staff and "is_default" in validated_data:
            validated_data.pop("is_default")

        return super().update(instance, validated_data)
