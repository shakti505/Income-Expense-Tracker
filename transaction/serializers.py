from rest_framework import serializers
from .models import Transaction
from budget.models import Budget
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db.models import F
from django.db import transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"

    def validate_user(self, value):
        user = self.context['request'].user
        if user.is_staff and value == user:
            raise serializers.ValidationError("Staff users cannot create transactions for themselves.")
        if not user.is_staff and value != user:
            raise serializers.ValidationError(" Staff users cannot create transactions for themselves")
        return value
    def validate_amount(self, value):
        """Validate the budget amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        if value > 999999999.99:
            raise serializers.ValidationError("Amount exceeds maximum allowed value")
        return value
    def validate_category(self, value):
        """Validate the category"""
        user = self.context['request'].user
        print(user)
        print(value.user)
        if value.user != user or value.is_deleted:
            raise serializers.ValidationError("Category does not belong to the user")

        if not value.type ==  self.initial_data['type']:
            raise serializers.ValidationError("Cannot create a debit transaction for a credit category")
        if value.is_deleted:
            raise serializers.ValidationError("Category is deleted")
        return value
    def validate(self, data):
        user = data.get('user')
        category = data.get('category')

        # Manually passed date or current date if not provided
        transaction_date = data.get('date', timezone.now().date())

        print(transaction_date)
        # Find user's budget for this category within the date range
      

    

        return data
