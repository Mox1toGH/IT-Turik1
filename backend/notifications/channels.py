import abc
import logging

from django.core.mail import send_mail
from django.conf import settings

from .models import Notification

logger = logging.getLogger(__name__)


class NotificationChannel(abc.ABC):
    """Abstract base class for notification delivery channels."""

    @abc.abstractmethod
    def send(self, *, recipient, title, message, event_type, email_subject=None):
        """
        Deliver a notification to *recipient*.

        Args:
            recipient:     User instance.
            title:         Short notification title.
            message:       Full notification body.
            event_type:    Event key from config.EVENTS.
            email_subject: Optional subject override for email channel.
        """


class SystemChannel(NotificationChannel):
    """Saves a Notification record in the database (in-site notification)."""

    def send(self, *, recipient, title, message, event_type, email_subject=None):
        Notification.objects.create(
            recipient=recipient,
            event_type=event_type,
            title=title,
            message=message,
        )


class EmailChannel(NotificationChannel):
    """Sends an email to the recipient via Django's email backend."""

    def send(self, *, recipient, title, message, event_type, email_subject=None):
        email = getattr(recipient, 'email', None)
        if not email:
            logger.warning(
                'EmailChannel: user %s has no email, skipping %s',
                recipient.id,
                event_type,
            )
            return

        subject = email_subject or title
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                'EmailChannel: failed to send %s to user %s (%s)',
                event_type,
                recipient.id,
                email,
            )


# Channel registry — maps channel name → class.
CHANNEL_REGISTRY = {
    'system': SystemChannel,
    'email': EmailChannel,
}
