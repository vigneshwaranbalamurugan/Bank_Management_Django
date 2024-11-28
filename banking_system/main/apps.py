from django.apps import AppConfig
from django.core.mail import send_mail

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    def ready(self):
        """
        Override this method to trigger email sending when the app is ready.
        Here we can call a function that sends emails or queues them.
        """
        # Trigger email sending automatically (e.g., send a welcome email to a user)
        self.send_automated_email()

    def send_automated_email(self):
        """
        A function that sends an email or queues it for later sending.
        In this example, we send a test email when the app starts.
        """
        subject = 'Automated Email Triggered on App Start'
        message = 'This is a test email automatically triggered by the app startup.'
        recipient_list = ['vigneshwaranb.22cse@kongu.edu']  # Replace with real recipients

        # Option 1: Directly send email using Django's `send_mail`
        send_mail(subject, message, 'vigneshwaranb.22cse@kongu.edu', recipient_list)

        