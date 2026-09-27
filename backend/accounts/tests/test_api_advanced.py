from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from backend.auth import authenticate

class AccountsApiAdvancedTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('acc_admin', 'a@e.com', 'pass', role='admin', is_staff=True)
        self.user1 = User.objects.create_user('acc_user1', 'u1@e.com', 'pass', full_name='User One')
        self.user2 = User.objects.create_user('acc_user2', 'u2@e.com', 'pass', full_name='User Two')

    # 15 tests
    def test_list_users_admin(self):
        url = reverse('ninja-api:users')
        authenticate(self.client, self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 2)

    def test_list_users_authenticated(self):
        url = reverse('ninja-api:users')
        authenticate(self.client, self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_anonymous_forbidden(self):
        url = reverse('ninja-api:users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_admin(self):
        url = reverse('ninja-api:user_detail', kwargs={'pk': self.user1.id})
        authenticate(self.client, self.admin)
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['username'], 'acc_user1')

    def test_retrieve_user_authenticated(self):
        url = reverse('ninja-api:user_detail', kwargs={'pk': self.user2.id})
        authenticate(self.client, self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_anonymous_forbidden(self):
        url = reverse('ninja-api:user_detail', kwargs={'pk': self.user1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_users(self):
        url = reverse('ninja-api:users') + '?search=acc_user1'
        authenticate(self.client, self.user2)
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'acc_user1')

    def test_search_users_not_found(self):
        url = reverse('ninja-api:users') + '?search=nobody'
        authenticate(self.client, self.user2)
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_create_user_endpoint_not_allowed(self):
        # Creating user usually done via registration endpoint, not user-list
        url = reverse('ninja-api:users')
        authenticate(self.client, self.admin)
        response = self.client.post(url, {'username': 'u3', 'password': 'p'})
        # Should be forbidden or method not allowed on user list if Djoser handles it
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN])
