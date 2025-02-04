import uuid
from django.db import models
from user.models import CustomUser


class Category(models.Model):
    """Creating table of Category"""
    CATEGORY_TYPES = (
        ("debit", "Debit"),
        ("credit", "Credit"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="categories",
      
    )
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)  # Add type field
    is_predefined = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)