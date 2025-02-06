# utils/tasks.py
from celery import shared_task
from django.utils import timezone
from budget.models import Budget
from transaction.models import Transaction
from services.notification import (
    NotificationService,
)  # Assuming your NotificationService is already set up
from django.db.models import Sum
from decimal import Decimal


@shared_task
def track_and_notify_budget(transaction_id):
    """
    Asynchronously track the budget and send a notification if the limit is reached.
    """
    try:
        # Fetch the transaction from the database by ID
        transaction = Transaction.objects.get(id=transaction_id)

        # Get the budget for the category and time of the transaction
        budget = Budget.objects.filter(
            user=transaction.user,
            category=transaction.category,
            year=transaction.date.year,
            month=transaction.date.month,
            is_deleted=False,
        ).first()

        # Calculate the total spending for the category and time period
        total_spent = Transaction.objects.filter(
            user=transaction.user,
            category=transaction.category,
            date__year=transaction.date.year,
            date__month=transaction.date.month,
            is_deleted=False,
        ).aggregate(Sum("amount"))["amount__sum"] or Decimal("0")
        print(budget.amount)
        print(total_spent)
        # Check if the spending has exceeded any thresholds
        total_spent_percentage = (total_spent / budget.amount) * 100
        print(total_spent_percentage)
        # Check for warning and critical thresholds
        if total_spent_percentage >= budget.CRITICAL_THRESHOLD:
            print(total_spent)
            send_budget_alert(budget, total_spent, transaction.amount, critical=True)
        elif total_spent_percentage >= budget.WARNING_THRESHOLD:
            print("Hello")
            send_budget_alert(budget, total_spent, transaction.amount)

        # Update the last warning sent time after notifying, use timezone.now() for timezone-aware datetime
        budget.last_warning_sent_at = timezone.now()
        budget.save()

    except Budget.DoesNotExist:
        pass  # No budget for this category/time, so do nothing


def send_budget_alert(budget, total_spent, new_spent, critical=False):
    """Send an email notification if the budget limit is reached or exceeded."""
    print("HEllo from send ")
    percentage = (total_spent / budget.amount) * 100
    subject = f"Budget Alert: {budget.category.name} - {percentage:.1f}% used"

    # If critical, mention in the subject line
    if critical:
        subject = (
            f"CRITICAL Budget Alert: {budget.category.name} - {percentage:.1f}% used"
        )

    # Prepare the email content
    content = (
        f"You have used {total_spent} out of {budget.amount} for category {budget.category.name}."
        f"\nCurrent spending is {new_spent}. Budget status: {'Critical' if critical else 'Warning'}."
    )

    # Send the email
    NotificationService.send_budget_alert(
        user_email=budget.user.email,
        category_name=budget.category.name,
        percentage=percentage,
        amount=budget.amount,
        spent=total_spent,
        subject=subject,
        content=content,
    )
