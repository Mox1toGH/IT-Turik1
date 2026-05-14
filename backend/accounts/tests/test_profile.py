from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, RoleActivationCode

VALID_GIF = (
    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
    b'\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
    b'\x00\x02\x02L\x01\x00;'
)

class ProfileTests(APITestCase):
    profile_url = reverse('profile')
    profile_avatar_url = reverse('profile_avatar')

    def test_profile_update_completes_onboarding(self):
        user = User.objects.create_user(
            username='googleuser',
            email='googleuser@example.com',
            password='StrongPass123!',
            needs_onboarding=True,
        )
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            self.profile_url,
            {
                'username': 'updatedgoogleuser',
                'role': 'team',
                'full_name': 'Updated Name',
                'phone': '+380991112233',
                'city': 'Kyiv',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.needs_onboarding)

    def test_profile_update_requires_redeem_code_for_restricted_role(self):
        user = User.objects.create(
            username='restricted', email='r@e.com', needs_onboarding=True, is_active=True, role='team'
        )
        user.set_unusable_password()
        user.save()
        self.client.force_authenticate(user=user)
        response = self.client.patch(self.profile_url, {'role': 'jury', 'password': 'Pass123!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_update_requires_password_for_google_onboarding(self):
        user = User.objects.create(username='no-pass', email='n@e.com', needs_onboarding=True, is_active=True)
        user.set_unusable_password()
        user.save()
        self.client.force_authenticate(user=user)
        response = self.client.patch(self.profile_url, {'role': 'team', 'full_name': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_update_sets_password_for_google_onboarding(self):
        user = User.objects.create(username='set-pass', email='s@e.com', needs_onboarding=True, is_active=True)
        user.set_unusable_password()
        user.save()
        self.client.force_authenticate(user=user)
        response = self.client.patch(self.profile_url, {'role': 'team', 'password': 'Pass123!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('Pass123!'))

    def test_profile_delete_removes_current_user(self):
        user = User.objects.create_user(username='delete-me', email='delete-me@example.com', password='StrongPass123!')
        self.client.force_authenticate(user=user)
        response = self.client.delete(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user.id).exists())

    def test_profile_avatar_upload_updates_avatar(self):
        user = User.objects.create_user(username='avatar-user', email='avatar-user@example.com', password='StrongPass123!')
        self.client.force_authenticate(user=user)
        avatar = SimpleUploadedFile('avatar.gif', VALID_GIF, content_type='image/gif')
        response = self.client.patch(self.profile_avatar_url, {'avatar': avatar}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(bool(user.avatar))

    def test_profile_avatar_delete_removes_avatar(self):
        user = User.objects.create_user(username='avatar-remove-user', email='a@e.com', password='P')
        user.avatar = SimpleUploadedFile('avatar.gif', VALID_GIF, content_type='image/gif')
        user.save()
        self.client.force_authenticate(user=user)
        response = self.client.delete(self.profile_avatar_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertFalse(bool(user.avatar))
