import uuid
from django.db import models
from user.models import CustomUser


class Category(models.Model):
    """Creating table of Category"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="categories",
        null=True,
        blank=True,
    )
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)
