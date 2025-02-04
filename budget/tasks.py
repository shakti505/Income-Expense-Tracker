# tasks.py
from celery import shared_task
from decimal import Decimal
from django.db.models import Sum
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from expense_tracker.secrets import SENDGRID_API_KEY

@shared_task
def check_budget_thresholds():
    """Check budgets and send notifications if threshold is reached"""
    from .models import Budget
    from transaction.models import Transaction
    
    # Get active budgets that haven't been notified
    budgets = Budget.objects.filter(
        is_deleted=False,
        is_notified=False
    ).select_related('user', 'category')
    print(budgets)
    
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=budget.user,
            category=budget.category,
            date__year=budget.year,
            date__month=budget.month,
            is_deleted=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        if budget.amount > 0:
            print(budget.amount)
            percentage_used = (spent / budget.amount) * 100
            if percentage_used >= budget.notification_threshold:
                send_budget_notification.delay(
                    budget.id,
                    budget.user.email,
                    budget.category.name,
                    float(percentage_used)
                )
                budget.is_notified = True
                budget.save(update_fields=['is_notified'])

@shared_task
def send_budget_notification(budget_id, email, category_name, percentage):
    """Send budget threshold notification email"""
    subject = f"Budget Alert: {category_name}"
    message = f"Your budget for {category_name} has reached {percentage:.1f}% of the allocated amount."
    
    send_email(
        'shakti@gkmit.co',
        [email],

    )



@staticmethod
def send_email(to_email):
    """Sends an email using SendGrid API"""
    message = Mail(
        from_email='shakti@gkmit.co',  # Must be verified in SendGrid
        to_emails=to_email,
    )

    message.template_id = 'd-ab22c01653ca4eabb78561b4ee10d3b9'

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)  # Use API key from settings
        response = sg.send(message)
        print("Hello mail is sended successfully to the user for budget")
        return response.status_code,   # 202 means email is sent
    except Exception as e:
        print(f"Email sending failed: {str(e)}")  # Log the error
        return None
    

# from celery import Celery
# from celery.schedules import crontab
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
# from django.utils import timezone

# app = Celery('expense_tracker')

# # Add periodic task
# def add_periodic_task():
#     # Ensure the schedule exists (e.g., every day at midnight)
#     schedule, created = IntervalSchedule.objects.get_or_create(
#         every=1,  # every 1 day
#         period=IntervalSchedule.DAYS,
#     )
    
#     PeriodicTask.objects.create(
#         interval=schedule,  # Use the above schedule
#         name='Check Budget Thresholds',
#         task='yourapp.tasks.check_budget_thresholds',  # The task to run
#         expires=timezone.now() + timezone.timedelta(days=1),  # Optional expiration
#     )