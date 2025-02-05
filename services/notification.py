from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Personalization, To
from expense_tracker.secrets import SENDGRID_API_KEY


class NotificationService:
    @classmethod
    def send_budget_alert(
        cls, user_email, category_name, percentage, amount, spent, subject, content
    ):
        """Send budget alert notification via email."""
        try:

            message = Mail(
                from_email="developer.shaktisingh@gmail.com",
                to_emails=user_email,
                subject=subject,
                plain_text_content=content,
            )

            # Set the SendGrid template ID
            # message.template_id = "d-888153bb49e34263a7c51b2cddfb8659"

            # Add dynamic template data
            # personalization = Personalization()
            # personalization.add_to(To(user_email))
            # personalization.dynamic_template_data = {
            #     "subject": subject,
            #     "content": content,
            #     "category_name": category_name,
            #     "percentage": f"{percentage:.1f}",
            #     "amount": f"{amount}",
            #     "spent": f"{spent}",
            # }
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"Email sent to {user_email}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending email: {e}")
