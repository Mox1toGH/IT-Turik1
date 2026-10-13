import logging

from django.db import transaction
from django.test import TestCase

from accounts.models import User
from notifications.models import (
    Notification,
    NotificationConfig,
    NotificationDeliveryTask,
    UserNotificationSettings,
)
from notifications.services import NotificationService

logger = logging.getLogger(__name__)


class NotificationServiceTests(TestCase):
    def test_notify_rolls_back_with_enclosing_transaction(self):
        user = User.objects.create_user(
            username='notification-rollback',
            email='notification-rollback@example.com',
        )

        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                NotificationService.notify(
                    recipients=[user],
                    event_type='news_published',
                    context={'news_id': 3, 'news_title': 'Rollback test'},
                )
                raise RuntimeError('roll back business action')

        self.assertFalse(Notification.objects.exists())
        self.assertFalse(NotificationDeliveryTask.objects.exists())

    def test_notify_respects_existing_user_preferences(self):
        users = User.objects.bulk_create(
            [
                User(
                    username=f'notification-pref-{index}',
                    email=f'notification-pref-{index}@example.com',
                )
                for index in range(3)
            ]
        )
        NotificationConfig.objects.create(
            user=users[0],
            event_type='news_published',
            is_system_enabled=False,
            is_email_enabled=True,
        )
        NotificationConfig.objects.create(
            user=users[1],
            event_type='news_published',
            is_system_enabled=True,
            is_email_enabled=False,
        )
        UserNotificationSettings.objects.create(
            user=users[2],
            emails_disabled_globally=True,
        )

        NotificationService.notify(
            recipients=users,
            event_type='news_published',
            context={'news_id': 2, 'news_title': 'Preferences test'},
        )

        self.assertEqual(
            list(
                Notification.objects.order_by('recipient_id').values_list(
                    'recipient_id',
                    flat=True,
                )
            ),
            [users[1].id, users[2].id],
        )
        self.assertEqual(
            list(
                NotificationDeliveryTask.objects.order_by(
                    'recipient_id'
                ).values_list('recipient_id', flat=True)
            ),
            [users[0].id],
        )
