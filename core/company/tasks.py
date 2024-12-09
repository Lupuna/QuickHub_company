from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def notify_users_created(emails):
    for email in emails:
        send_mail(
            subject="Welcome!",
            message=f"Hello {email}, you have been added!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD
        )
