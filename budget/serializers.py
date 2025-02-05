from datetime import date
from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from .models import Budget
from user.models import CustomUser
from category.models import Category
from transaction.models import Transaction  # Import Transaction model
from rest_framework.exceptions import ValidationError


class BudgetSerializer(serializers.ModelSerializer):
    month_year = serializers.CharField(write_only=True)
    spent_amount = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "amount",
            "month_year",
            "user",
            "category",
            "spent_amount",
            "year",
            "month",
            "is_deleted",
        ]
        read_only_fields = [
            "id",
            "year",
            "month",
            "is_deleted",
            "spent_amount",
        ]

    def __init__(self, *args, **kwargs):
        request = kwargs.get("context", {}).get("request", None)

        if request.method == "PATCH":
            self.fields["user"].read_only = True
            self.fields["month_year"].read_only = True
            self.fields["category"].read_only = True

        super().__init__(*args, **kwargs)

    def validate_category(self, value):
        """Validate category"""
        if not value:
            raise ValidationError("Category is required")
        if value.is_deleted:
            raise ValidationError("Not Found")
        if value.type != "debit":
            raise ValidationError("Budget can only be created for debit categories")
        request = self.context.get("request")
        user = request.user if request else None
        if not user.is_staff:
            # Regular users can only use their categories or predefined categories
            if not (value.is_predefined or value.user_id == user.id):
                raise ValidationError(
                    "You can only create budgets for your categories or predefined categories"
                )
        return value

    def validate_month_year(self, value):
        """Validate month_year format and value"""
        try:
            parts = value.split("-")
            if len(parts) != 2:
                raise ValueError("Invalid format")

            month = int(parts[0])
            year = int(parts[1])

            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")

            if not (2000 <= year <= 2100):
                raise ValueError("Year must be between 2000 and 2100")

            today = date.today()
            budget_date = date(year, month, 1)

            if budget_date < date(today.year, today.month, 1):
                raise ValueError("Cannot create budget for past months")

            self._validated_month = month
            self._validated_year = year

            return value

        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid format. Use M-YYYY or MM-YYYY (e.g., 2-2024 or 02-2024). {str(e)}"
            )

    def validate_user(self, value):
        """Validate user permissions"""
        request = self.context.get("request")
        if not request:
            raise ValidationError("Request context is required")

        current_user = request.user
        target_user_id = value.id if isinstance(value, CustomUser) else value

        if current_user.is_staff:
            if target_user_id == current_user.id:
                raise ValidationError(
                    "Staff members cannot create budgets for themselves"
                )

            target_user = CustomUser.objects.filter(
                id=target_user_id, is_active=True
            ).first()
            if not target_user:
                raise ValidationError("Target user must be active")
        else:
            if target_user_id != current_user.id:
                raise ValidationError("You can only create a budget for yourself")

        return value

    def validate(self, data):
        """Cross-field validation"""
        data = super().validate(data)

        # Check for duplicate budget
        if self.instance is None:  # Only for creation
            existing_budget = Budget.objects.filter(
                user=data["user"],
                category=data["category"],
                year=self._validated_year,
                month=self._validated_month,
                is_deleted=False,
            ).exists()

            if existing_budget:
                raise ValidationError(
                    {
                        "month_year": f"A budget already exists for {self._validated_month}-{self._validated_year} "
                        f"in this category"
                    }
                )

        return data

    def create(self, validated_data):
        """Create budget and update exhausted amount from existing transactions"""
        validated_data.pop("month_year", None)
        validated_data["month"] = self._validated_month
        validated_data["year"] = self._validated_year
        print(self._validated_month)
        print(self._validated_year)

        # Create the budget
        budget = super().create(validated_data)

        # Update exhausted amount from existing transactions
        # self._update_exhausted_amount(budget)

        return budget

    def update(self, instance, validated_data):
        """Update budget and recalculate exhausted amount"""
        budget = super().update(instance, validated_data)

        # Update exhausted amount from existing transactions

        return budget

    def get_spent_amount(self, obj):
        """Get current spent amount for budget"""
        from transaction.models import Transaction

        spent = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            date__year=obj.year,
            date__month=obj.month,
            is_deleted=False,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        return str(spent)
