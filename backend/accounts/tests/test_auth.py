from unittest.mock import patch
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User

@override_settings(GOOGLE_OAUTH_CLIENT_ID='test-google-client-id')
class GoogleAuthViewTests(APITestCase):
    url = reverse('google_login')

    @patch('accounts.serializers.id_token.verify_oauth2_token')
    def test_google_login_creates_user_and_returns_jwt(self, mocked_verify):
        mocked_verify.return_value = {
            'iss': 'https://accounts.google.com',
            'email': 'new.user@example.com',
            'email_verified': True,
            'name': 'New User',
        }
        response = self.client.post(self.url, {'id_token': 'fake-token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(response.data['onboarding_required'])
        created_user = User.objects.get(email='new.user@example.com')
        self.assertTrue(created_user.is_active)
        self.assertEqual(created_user.full_name, 'New User')

    @patch('accounts.serializers.id_token.verify_oauth2_token')
    def test_google_login_activates_existing_user(self, mocked_verify):
        existing = User.objects.create_user(
            username='existing', email='existing@example.com', password='StrongPass123!', is_active=False,
        )
        mocked_verify.return_value = {
            'iss': 'accounts.google.com',
            'email': 'existing@example.com',
            'email_verified': True,
            'name': 'Existing User',
        }
        response = self.client.post(self.url, {'id_token': 'fake-token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['onboarding_required'])
        existing.refresh_from_db()
        self.assertTrue(existing.is_active)

    @patch('accounts.serializers.id_token.verify_oauth2_token')
    def test_google_login_rejects_unverified_email(self, mocked_verify):
        mocked_verify.return_value = {
            'iss': 'https://accounts.google.com',
            'email': 'user@example.com',
            'email_verified': False,
        }
        response = self.client.post(self.url, {'id_token': 'fake-token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_google_login_requires_token(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetFlowTests(APITestCase):
    request_url = reverse('password_reset_request')

    @staticmethod
    def _get_uid_and_token(user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    def test_password_reset_request_sends_email(self):
        user = User.objects.create_user(
            username='reset-user', email='reset-user@example.com', password='StrongPass123!', is_active=True,
        )
        response = self.client.post(self.request_url, {'email': user.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].content_subtype, 'html')
        self.assertIn('Reset your password', mail.outbox[0].body)
        self.assertIn('TournamentOS', mail.outbox[0].body)

    def test_password_reset_request_rejects_nonexistent_email(self):
        response = self.client.post(self.request_url, {'email': 'missing@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request_uses_authenticated_user_email_when_email_not_provided(self):
        user = User.objects.create_user(
            username='auth-reset-user',
            email='auth-reset-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self.request_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset your password', mail.outbox[0].body)

    def test_password_reset_confirm_get_rejects_invalid_or_expired_link(self):
        user = User.objects.create_user(username='invalid-link-user', email='i@e.com', password='P', is_active=True)
        uid, _ = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': 'invalid'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_get_accepts_valid_link(self):
        user = User.objects.create_user(username='valid-link-user', email='v@e.com', password='P', is_active=True)
        uid, token = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_post_updates_password(self):
        user = User.objects.create_user(
            username='confirm-reset-user', email='confirm-reset-user@example.com', password='StrongPass123!', is_active=True,
        )
        uid, token = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.post(
            url, {'new_password': 'NewStrongPass123!', 'confirm_password': 'NewStrongPass123!'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewStrongPass123!'))

class ChangePasswordFlowTests(APITestCase):
    change_url = reverse('change_password')

    def setUp(self):
        self.user = User.objects.create_user(
            username='change-password-user', email='change-password-user@example.com', password='StrongPass123!', is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        response = self.client.post(
            self.change_url,
            {
                'current_password': 'StrongPass123!',
                'new_password': 'EvenStrongerPass456!',
                'confirm_password': 'EvenStrongerPass456!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('EvenStrongerPass456!'))
