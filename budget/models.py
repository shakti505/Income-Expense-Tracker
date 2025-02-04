from django.db import models

# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import CustomUser
from category.models import Category
from utils.models import BaseModel, SoftDeleteModel
from datetime import date
import calendar

class Budget(BaseModel, SoftDeleteModel):
    """Budget model with notification threshold"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="Month must be between 1 and 12"),
            MaxValueValidator(12, message="Month must be between 1 and 12")
        ]
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    notification_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=90.00,
    )
    is_notified = models.BooleanField(default=False, help_text="Indicates if notification has been sent")

    class Meta:
        ordering = ["-year", "-month"]
        unique_together = ['user', 'category', 'year', 'month', 'is_deleted']

    def __str__(self):
        return f"{self.name} - {self.month}/{self.year}"

