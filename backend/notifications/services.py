import logging

from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError

from .channels import CHANNEL_REGISTRY
from .config import EVENTS
from .dispatcher import dispatch_pending_async
from .models import NotificationDeliveryTask

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Central entry-point for sending notifications.

    Usage::

        from notifications.services import NotificationService

        NotificationService.notify(
            recipients=[user],
            event_type='team_invitation_received',
            context={'team_name': team.name, 'invited_by': captain.username},
        )
    """

    @classmethod
    def notify(cls, *, recipients, event_type, context=None):
        """
        Dispatch a notification to *recipients* for the given *event_type*.
        """
        from .models import NotificationConfig, UserNotificationSettings
        
        event = EVENTS.get(event_type)
        if not event:
            logger.warning('NotificationService: unknown event_type=%s', event_type)
            return

        # Format content once for all recipients
        title, message, email_subject = event.format(context)

        tasks_to_create = []

        for recipient in recipients:
            # 1. Fetch or create the personal settings for this user
            user_settings, _ = UserNotificationSettings.objects.get_or_create(user=recipient)
            
            # 2. Fetch or create the personal config for this event
            db_config, _ = NotificationConfig.objects.get_or_create(
                user=recipient,
                event_type=event_type,
                defaults={
                    'is_system_enabled': 'system' in event.channels,
                    'is_email_enabled': 'email' in event.channels
                }
            )

            # 3. Determine active channels for THIS user
            active_channels = []
            if db_config.is_system_enabled:
                active_channels.append('system')
            
            # Email only if enabled in event AND not disabled globally for user
            if db_config.is_email_enabled and not user_settings.emails_disabled_globally:
                active_channels.append('email')

            for channel_name in active_channels:
                if channel_name not in CHANNEL_REGISTRY:
                    continue
                tasks_to_create.append(
                    NotificationDeliveryTask(
                        recipient=recipient,
                        channel=channel_name,
                        event_type=event_type,
                        title=title,
                        message=message,
                        email_subject=email_subject or '',
                    )
                )

        if not tasks_to_create:
            return

        try:
            NotificationDeliveryTask.objects.bulk_create(tasks_to_create)
            transaction.on_commit(dispatch_pending_async)
        except (OperationalError, ProgrammingError):
            logger.exception(
                'Notification queue table is unavailable. Falling back to inline delivery.'
            )
            for task in tasks_to_create:
                channel_cls = CHANNEL_REGISTRY.get(task.channel)
                if not channel_cls:
                    continue
                try:
                    channel = channel_cls()
                    channel.send(
                        recipient=task.recipient,
                        title=task.title,
                        message=task.message,
                        event_type=task.event_type,
                        email_subject=task.email_subject,
                    )
                except Exception:
                    logger.exception(
                        'Inline fallback notification delivery failed: user=%s event=%s channel=%s',
                        getattr(task.recipient, 'id', None),
                        task.event_type,
                        task.channel,
                    )
