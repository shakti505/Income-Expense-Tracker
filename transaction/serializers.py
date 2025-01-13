from rest_framework import serializers
from .models import Transaction, Category
from rest_framework.exceptions import ValidationError


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ["is_deleted", "user"]

    def validate_category(self, category):
        """
        Validates the category to ensure it belongs to the user or is a default category
        and is not marked as deleted.
        """
        user = self.context["request"].user

        if category and category.user != user and not category.is_default:
            raise ValidationError(
                {
                    "category": "You can only use your own categories or default categories."
                }
            )

        if category and category.is_deleted:
            raise ValidationError(
                {"category": "This category is no longer available (deleted)."}
            )

        return category

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user

        category = validated_data.get("category")
        if category:
            self.validate_category(category)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user

        # Validate category during update
        category = validated_data.get("category")
        if category:
            self.validate_category(category)

        return super().update(instance, validated_data)
