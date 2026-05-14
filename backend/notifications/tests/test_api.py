from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from notifications.models import Notification, UserNotificationSettings, NotificationConfig
from accounts.models import User

class NotificationApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', email='u@e.com', password='pass')
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('notification-list')

    def test_list_notifications(self):
        Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unread_count(self):
        Notification.objects.create(recipient=self.user, title='T1', event_type='e', is_read=False)
        url = reverse('notification-unread-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_mark_read(self):
        notif = Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('notification-mark-read', kwargs={'pk': notif.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_all_read(self):
        Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('notification-mark-all-read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)

    def test_delete_notification(self):
        notif = Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('notification-delete', kwargs={'pk': notif.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(id=notif.id).exists())

    def test_delete_all_notifications(self):
        Notification.objects.create(recipient=self.user, title='T1', event_type='e')
        url = reverse('notification-delete-all')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.filter(recipient=self.user).count(), 0)

    def test_get_settings(self):
        url = reverse('notification-settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_global_settings(self):
        url = reverse('notification-settings-global-update')
        response = self.client.patch(url, {'emails_disabled_globally': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.notification_settings.refresh_from_db()
        self.assertTrue(self.user.notification_settings.emails_disabled_globally)

    def test_update_event_config(self):
        url = reverse('notification-settings-config-update')
        response = self.client.patch(url, {'event_type': 'test', 'is_email_enabled': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        config = NotificationConfig.objects.get(user=self.user, event_type='test')
        self.assertFalse(config.is_email_enabled)

    def test_notification_list_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
