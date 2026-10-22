import logging

from django.db import connection, transaction
from django.db.utils import OperationalError, ProgrammingError

from .channels import CHANNEL_REGISTRY
from .config import EVENTS
from .dispatcher import dispatch_pending_async
from .models import Notification, NotificationDeliveryTask
from .realtime import emit_notifications_created

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

        title, message, email_subject = event.format(context)
        recipient_ids = []
        recipients_by_id = {}
        for recipient in recipients:
            recipient_ids.append(recipient.id)
            recipients_by_id[recipient.id] = recipient

        if not recipient_ids:
            return

        settings_by_user = {
            setting.user_id: setting
            for setting in UserNotificationSettings.objects.filter(
                user_id__in=recipient_ids
            )
        }
        config_by_user = {
            config.user_id: config
            for config in NotificationConfig.objects.filter(
                user_id__in=recipient_ids,
                event_type=event_type,
            )
        }

        notifications_to_create = []
        tasks_to_create = []
        for recipient_id in recipient_ids:
            config = config_by_user.get(recipient_id)
            system_enabled = (
                config.is_system_enabled
                if config
                else 'system' in event.channels
            )
            email_enabled = (
                config.is_email_enabled
                if config
                else 'email' in event.channels
            )
            user_settings = settings_by_user.get(recipient_id)

            if system_enabled and 'system' in CHANNEL_REGISTRY:
                notifications_to_create.append(
                    Notification(
                        recipient_id=recipient_id,
                        event_type=event_type,
                        title=title,
                        message=message,
                    )
                )

            if (
                email_enabled
                and not (user_settings and user_settings.emails_disabled_globally)
                and 'email' in CHANNEL_REGISTRY
            ):
                tasks_to_create.append(
                    NotificationDeliveryTask(
                        recipient_id=recipient_id,
                        channel='email',
                        event_type=event_type,
                        title=title,
                        message=message,
                        email_subject=email_subject or '',
                    )
                )

        if not notifications_to_create and not tasks_to_create:
            return

        queue_unavailable = False
        with transaction.atomic(savepoint=not connection.in_atomic_block):
            if notifications_to_create:
                Notification.objects.bulk_create(notifications_to_create)
            if tasks_to_create:
                try:
                    with transaction.atomic():
                        NotificationDeliveryTask.objects.bulk_create(tasks_to_create)
                except (OperationalError, ProgrammingError):
                    queue_unavailable = True
                    logger.exception(
                        'Notification queue table is unavailable. Falling back to inline email delivery.'
                    )

        if queue_unavailable:
            for task in tasks_to_create:
                channel_cls = CHANNEL_REGISTRY.get(task.channel)
                if not channel_cls:
                    continue
                try:
                    channel = channel_cls()
                    channel.send(
                        recipient=recipients_by_id[task.recipient_id],
                        title=task.title,
                        message=task.message,
                        event_type=task.event_type,
                        email_subject=task.email_subject,
                    )
                except Exception:
                    logger.exception(
                        'Inline fallback notification delivery failed: user=%s event=%s channel=%s',
                        task.recipient_id,
                        task.event_type,
                        task.channel,
                    )
        elif tasks_to_create:
            transaction.on_commit(dispatch_pending_async)

        if notifications_to_create:
            transaction.on_commit(
                lambda: emit_notifications_created(notifications_to_create)
            )
