import logging

from .channels import CHANNEL_REGISTRY
from .config import EVENTS

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
                channel_cls = CHANNEL_REGISTRY.get(channel_name)
                if not channel_cls:
                    continue

                channel = channel_cls()
                channel.send(
                    recipient=recipient,
                    title=title,
                    message=message,
                    event_type=event_type,
                    email_subject=email_subject,
                )
