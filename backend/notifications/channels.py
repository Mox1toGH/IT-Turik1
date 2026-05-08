import abc
import logging
import re

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import Notification

logger = logging.getLogger(__name__)

# Map raw event_type keys to human-readable labels for the email badge
EVENT_TYPE_LABELS = {
    'team_invitation_received': 'Team Invitation',
    'team_invitation_accepted': 'Invitation Accepted',
    'team_invitation_declined': 'Invitation Declined',
    'team_join_request_received': 'Join Request',
    'team_join_request_accepted': 'Join Request Approved',
    'team_join_request_declined': 'Join Request Declined',
    'team_member_removed': 'Membership Update',
    'team_member_left': 'Membership Update',
}

# Events that go to /teams (general) — cannot link to a specific team
_GENERAL_TEAMS_EVENTS = {
    'team_invitation_received',   # recipient hasn't joined yet
}

# Button labels per event
EVENT_ACTION_LABELS = {
    'team_invitation_received':   'View Teams',
    'team_invitation_accepted':   'View Team',
    'team_invitation_declined':   'View Team',
    'team_join_request_received': 'Manage Requests',
    'team_join_request_accepted': 'View Team',
    'team_join_request_declined': 'View Teams',
    'team_member_removed':        'Browse Teams',
    'team_member_left':           'View Team',
}


def _get_action(event_type: str, message: str) -> tuple[str, str]:
    """Return (label, path) for the CTA button.

    Uses the same logic as the frontend getRedirectUrl():
    - team_invitation_received → /teams
    - everything else         → /teams/<team_id>  (extracted from message tag)
    """
    label = EVENT_ACTION_LABELS.get(event_type, 'Open Platform')

    if event_type in _GENERAL_TEAMS_EVENTS:
        return label, '/teams'

    # Try to extract team_id from [team:id:name:visibility] tag
    match = re.search(r'\[team:(\d+):', message)
    if match:
        return label, f'/teams/{match.group(1)}'

    return label, '/teams'


def _strip_notification_tags(text: str) -> str:
    """Convert [user:id:name] and [team:id:name:visibility] tags to plain names."""
    text = re.sub(r'\[user:\d+:(.+?)\]', r'\1', text)
    text = re.sub(r'\[team:\d+:(.+?)(?::(?:public|private))?\]', r'\1', text)
    return text


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
    """Sends a rich HTML email to the recipient via Django's email backend."""

    def send(self, *, recipient, title, message, event_type, email_subject=None):
        email = getattr(recipient, 'email', None)
        if not email:
            logger.warning(
                'EmailChannel: user %s has no email, skipping %s',
                recipient.id,
                event_type,
            )
            return

        site_url = getattr(settings, 'SITE_URL', 'http://localhost:5173')
        action_label, action_path = _get_action(event_type, message)

        plain_message = _strip_notification_tags(message)

        context = {
            'subject': email_subject or title,
            'title': title,
            'message': plain_message,
            'event_type_label': EVENT_TYPE_LABELS.get(event_type, event_type.replace('_', ' ').title()),
            'action_url': f'{site_url}{action_path}',
            'action_label': action_label,
            'unsubscribe_url': f'{site_url}/profile/notifications',
        }

        html_message = render_to_string('notifications/email_notification.html', context)

        subject = email_subject or title
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
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
