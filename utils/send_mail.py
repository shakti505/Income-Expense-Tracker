from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from expense_tracker.secrets import SENDGRID_API_KEY

def send_email(to_email, reset_link):
    """Sends an email using SendGrid API"""
    message = Mail(
        from_email='shakti@gkmit.co',  # Must be verified in SendGrid
        to_emails=to_email,
    )
    dynamic_template_data = {
        "reset_link": reset_link
    }
    message.dynamic_template_data = dynamic_template_data
    message.template_id = "d-36f7a9ccf47a4a199e7acb16f3c1f0e6"

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)  # Use API key from settings
        response = sg.send(message)
        print("Hello mail is sended successfully to the user")
        return response.status_code,   # 202 means email is sent
    except Exception as e:
        print(f"Email sending failed: {str(e)}")  # Log the error
        return None
