from django.apps import AppConfig


class BudgetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budget'

    def ready(self):
        from .tasks import add_periodic_task
        add_periodic_task()