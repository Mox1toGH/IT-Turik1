from django.test import TestCase
from django.utils import timezone
from notifications.models import Notification, UserNotificationSettings, NotificationConfig
from accounts.models import User

class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notif-u', email='n@e.com')

    def test_notification_str(self):
        notif = Notification.objects.create(recipient=self.user, event_type='test', title='Hello')
        self.assertEqual(str(notif), f'test → {self.user.id} (read=False)')

    def test_user_settings_str(self):
        settings = UserNotificationSettings.objects.create(user=self.user)
        self.assertEqual(str(settings), f"Settings for {self.user.username}")

    def test_notification_config_str(self):
        config = NotificationConfig.objects.create(user=self.user, event_type='test_event')
        self.assertEqual(str(config), f"{self.user.username} - test_event")

    def test_notification_is_read_default_false(self):
        notif = Notification.objects.create(recipient=self.user, event_type='test', title='Hello')
        self.assertFalse(notif.is_read)

    def test_user_settings_email_disabled_default_false(self):
        settings = UserNotificationSettings.objects.create(user=self.user)
        self.assertFalse(settings.emails_disabled_globally)

    def test_notification_config_defaults(self):
        config = NotificationConfig.objects.create(user=self.user, event_type='test')
        self.assertTrue(config.is_system_enabled)
        self.assertTrue(config.is_email_enabled)

    def test_notification_cascade_on_user_delete(self):
        Notification.objects.create(recipient=self.user, event_type='test', title='H')
        self.user.delete()
        self.assertEqual(Notification.objects.count(), 0)

    def test_notification_config_unique_together(self):
        from django.db import IntegrityError
        NotificationConfig.objects.create(user=self.user, event_type='test')
        with self.assertRaises(IntegrityError):
            NotificationConfig.objects.create(user=self.user, event_type='test')

    def test_user_settings_one_to_one(self):
        from django.db import IntegrityError
        UserNotificationSettings.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            UserNotificationSettings.objects.create(user=self.user)

    def test_notification_ordering(self):
        n1 = Notification.objects.create(recipient=self.user, event_type='t1', title='1')
        n2 = Notification.objects.create(recipient=self.user, event_type='t2', title='2')
        Notification.objects.filter(pk=n1.pk).update(created_at=timezone.now() - timezone.timedelta(minutes=1))
        Notification.objects.filter(pk=n2.pk).update(created_at=timezone.now())
        notifs = Notification.objects.all()
        self.assertEqual(notifs[0], n2)  # Order is -created_at
