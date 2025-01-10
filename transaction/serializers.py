from rest_framework import serializers
from .models import Transaction, Category
from rest_framework.exceptions import ValidationError


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ["is_deleted", "user"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        # Validate category
        category = validated_data.get("category")

        if category and category.user != user and not category.is_default:
            raise ValidationError(
                {
                    "category": "You can only use your own categories or default categories."
                }
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Validate category during update
        user = self.context["request"].user

        category = validated_data.get("category")
        if category and category.user != user and not category.is_default:
            raise ValidationError(
                {
                    "category": "You can only use your own categories or default categories."
                }
            )

        return super().update(instance, validated_data)
