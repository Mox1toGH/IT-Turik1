import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(name="accounts.send_html_email", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_html_email_task(subject: str, template_name: str, context: dict, recipient: str) -> None:
    """Send a rendered HTML email outside the request/response cycle."""
    html_message = render_to_string(template_name, context)
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.content_subtype = "html"
    email.send()


@shared_task(name="accounts.sync_google_calendar", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def sync_google_calendar_task(user_id: int) -> None:
    """Push all tournaments/events/rounds to the user's Google Calendar."""
    from .google_calendar import sync_all_calendar_items
    from .models import User

    user = User.objects.get(pk=user_id)
    sync_all_calendar_items(user)
