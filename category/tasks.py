from celery import shared_task
from datetime import datetime

from time import sleep

@shared_task
def print_current_time():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    print(f"Current Time: {now}")
    return now

@shared_task
def sum_two_numbers(a, b):
    print(f"Sum of {a} and {b} is {a + b}")
    return a + b




