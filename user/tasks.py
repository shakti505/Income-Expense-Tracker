
from celery import shared_task
from datetime import datetime
from utils.send_mail import send_email



@shared_task
def send_email_task(to_email, reset_link):
    print(f"Sending email to {to_email} with subject: {reset_link}")
    return send_email(to_email,reset_link )