"""Modles of Transactions app"""

import uuid
from django.db import models
from user.models import User
from category.models import Category


class Transaction(models.Model):
    """Creating table of Transactions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_CHOICES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.transaction_type} - {self.amount}"
