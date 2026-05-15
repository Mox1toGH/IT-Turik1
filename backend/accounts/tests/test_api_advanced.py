from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User

class AccountsApiAdvancedTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('acc_admin', 'a@e.com', 'pass', role='admin', is_staff=True)
        self.user1 = User.objects.create_user('acc_user1', 'u1@e.com', 'pass', full_name='User One')
        self.user2 = User.objects.create_user('acc_user2', 'u2@e.com', 'pass', full_name='User Two')

    # 15 tests
    def test_list_users_admin(self):
        url = reverse('user-list')
        self.client.force_authenticate(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertGreaterEqual(len(data), 3)

    def test_list_users_authenticated(self):
        url = reverse('user-list')
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_anonymous_forbidden(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_admin(self):
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        self.client.force_authenticate(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'acc_user1')

    def test_retrieve_user_authenticated(self):
        url = reverse('user-detail', kwargs={'pk': self.user2.id})
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_anonymous_forbidden(self):
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_admin(self):
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        self.client.force_authenticate(self.admin)
        response = self.client.patch(url, {'full_name': 'Updated One'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.full_name, 'Updated One')

    def test_update_user_self(self):
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.patch(url, {'full_name': 'Self Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.full_name, 'Self Updated')

    def test_update_user_other_forbidden(self):
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        self.client.force_authenticate(self.user2)
        response = self.client.patch(url, {'full_name': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_admin(self):
        url = reverse('user-detail', kwargs={'pk': self.user2.id})
        self.client.force_authenticate(self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user2.id).exists())

    def test_delete_user_self_forbidden(self):
        # Or maybe allowed depending on app rules, usually users can't delete themselves via generic delete without special endpoint
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_other_forbidden(self):
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        self.client.force_authenticate(self.user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_users(self):
        url = reverse('user-list') + '?search=acc_user1'
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'acc_user1')

    def test_search_users_not_found(self):
        url = reverse('user-list') + '?search=nobody'
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 0)

    def test_create_user_endpoint_not_allowed(self):
        # Creating user usually done via registration endpoint, not user-list
        url = reverse('user-list')
        self.client.force_authenticate(self.admin)
        response = self.client.post(url, {'username': 'u3', 'password': 'p'})
        # Should be forbidden or method not allowed on user list if Djoser handles it
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN])
