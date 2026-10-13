from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from notifications.models import Notification, UserNotificationSettings, NotificationConfig
from accounts.models import User
from backend.auth import authenticate

class NotificationApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', email='u@e.com', password='pass')
        authenticate(self.client, self.user)
        self.list_url = reverse('ninja-api:notification-list')

    def test_list_notifications(self):
        Notification.objects.all().delete()
        Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['items']), 1)

    def test_unread_count(self):
        Notification.objects.create(recipient=self.user, title='T1', event_type='e', is_read=False)
        url = reverse('ninja-api:notification-unread-count')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['unread_count'], 1)

    def test_mark_read(self):
        notif = Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('ninja-api:notification-mark-read', kwargs={'notification_id': notif.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_all_read(self):
        Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('ninja-api:notification-mark-all-read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)

    def test_delete_notification(self):
        notif = Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('ninja-api:notification-delete', kwargs={'notification_id': notif.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(id=notif.id).exists())

    def test_delete_all_notifications(self):
        Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('ninja-api:notification-delete-all')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(recipient=self.user).count(), 0)

    def test_get_settings(self):
        self.assertFalse(
            NotificationConfig.objects.filter(user=self.user).exists()
        )
        self.assertFalse(
            UserNotificationSettings.objects.filter(user=self.user).exists()
        )

        url = reverse('ninja-api:notification-settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['global_config']['emails_disabled_globally'], False)
        self.assertGreater(len(response.json()['configs']), 0)

    def test_update_global_settings(self):
        url = reverse('ninja-api:notification-settings-global-update')
        response = self.client.post(url, {'emails_disabled_globally': True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.notification_settings.refresh_from_db()
        self.assertTrue(self.user.notification_settings.emails_disabled_globally)

    def test_update_event_config(self):
        url = reverse('ninja-api:notification-settings-config-update')
        NotificationConfig.objects.create(user=self.user, event_type='test')
        response = self.client.post(url, {'event_type': 'test', 'is_email_enabled': False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        config = NotificationConfig.objects.get(user=self.user, event_type='test')
        self.assertFalse(config.is_email_enabled)

    def test_notification_list_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
