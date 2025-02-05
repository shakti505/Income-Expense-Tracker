# from django.apps import AppConfig

# import django
# from django.conf import settings
# from django.apps import apps

# # Set up the Django settings if not already done
# # django.setup()

# # Now it's safe to access models
# # Budget = apps.get_model("budget", "Budget")


# class TransactionConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "transaction"


# # You can now use the Budget model safely here

from django.apps import AppConfig


class TransactionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transaction"
