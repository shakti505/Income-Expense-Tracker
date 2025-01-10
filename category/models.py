import uuid
from django.db import models
from user.models import User

# from django.db.models.signals import pre_delete
# from django.dispatch import receiver


class Category(models.Model):
    """Creating table of Category"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="categories",
        null=True,
        blank=True,
    )
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


# @receiver(pre_delete, sender=User)
# def handle_user_pre_delete(sender, instance, **kwargs):
#     if instance.is_staff:
#         # Set user field to None for related categories
#         Category.objects.filter(user=instance).update(user=None)
#     else:
#         # Soft delete categories by marking them as deleted
#         Category.objects.filter(user=instance).update(is_deleted=True)
