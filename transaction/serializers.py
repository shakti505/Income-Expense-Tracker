from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Transaction, Category


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model.
    Handles validation, creation, and updating of transactions.
    """

    class Meta:
        model = Transaction
        exclude = ["is_deleted"]  # Exclude the `is_deleted` field from serialization

    def validate_category(self, category):
        """
        Validate the category to ensure it belongs to the user or is a default category.
        Also ensures the category is not deleted.
        """
        user = self.context["request"].user

        # Check if the category belongs to the user or is a default category
        if category and category.user != user and not category.is_default:
            raise ValidationError(
                {
                    "category": "You can only use your own categories or default categories."
                }
            )

        # Check if the category is deleted
        if category and category.is_deleted:
            raise ValidationError(
                {"category": "This category is no longer available (deleted)."}
            )

        return category

    def validate(self, data):
        """
        Validate the transaction data before creation or update.
        """
        user = self.context["request"].user

        # Ensure normal users cannot create or update transactions for other users
        if not user.is_staff and "user" in data and data["user"] != user:
            raise ValidationError(
                {
                    "user": "You do not have permission to create or update transactions for other users."
                }
            )

        return data

    def create(self, validated_data):
        """
        Create a new transaction.
        """
        user = self.context["request"].user

        # If the user is not staff, ensure the transaction is created for themselves
        if not user.is_staff:
            validated_data["user"] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing transaction.
        """
        user = self.context["request"].user

        # If the user is not staff, ensure they can only update their own transactions
        if not user.is_staff and instance.user != user:
            raise ValidationError(
                {"user": "You do not have permission to update this transaction."}
            )

        return super().update(instance, validated_data)
