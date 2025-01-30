from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')

app = Celery('expense_tracker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'print-current-time-every-minute': {
        'task': 'category.tasks.print_current_time',  # Correct task path
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
}

# Load task modules from all registered Django app configs.

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')