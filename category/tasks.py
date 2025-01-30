from celery import shared_task
from datetime import datetime
from .send_email import send_email
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


@shared_task
def send_email_task(to_email, subject):
    print(f"Sending email to {to_email} with subject: {subject}")
    return send_email(to_email, subject)

