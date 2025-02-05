# # services/notification.py

# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from expense_tracker.secrets import SENDGRID_API_KEY


# class NotificationService:
#     @classmethod
#     def send_budget_alert(cls, user_email, category_name, percentage, amount, spent):
#         """Send budget alert notification via email."""
#         try:
#             subject = f"Budget Alert: {category_name} - {percentage:.1f}% used"
#             content = (
#                 f"You have used {spent} out of {amount} for category {category_name}."
#             )

#             message = Mail(
#                 from_email="your_email@example.com",
#                 to_emails=user_email,
#                 subject=subject,
#                 plain_text_content=content,
#             )

#             sg = SendGridAPIClient(SENDGRID_API_KEY)
#             response = sg.send(message)
#             print(f"Email sent to {user_email}, status code: {response.status_code}")
#         except Exception as e:
#             print(f"Error sending email: {e}")
