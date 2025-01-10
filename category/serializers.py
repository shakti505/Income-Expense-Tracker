from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "user", "is_default")
        # write_only_fields = ["user"]
        extra_kwargs = {"user": {"write_only": True}}

    def validate_name(self, value):
        user = self.context["request"].user

        # Check if a category with the same name exists for the same user
        if Category.objects.filter(
            name__iexact=value, user=user, is_deleted=False
        ).exists():
            raise serializers.ValidationError(
                "A category with this name already exists for this user. Names are case-insensitive."
            )
        # Check if a category with the same name exists for any staff user
        if Category.objects.filter(
            name__iexact=value, user__is_staff=True, is_deleted=False
        ).exists():
            raise serializers.ValidationError(
                "A category with this name already exists for a staff user. Names are case-insensitive."
            )

        # Check if a category with the same name exists for any null user
        if Category.objects.filter(name__iexact=value, user__is_staff=None).exists():
            raise serializers.ValidationError(
                "A category with this name already exists for a Null user. Names are case-insensitive."
            )

        return value
