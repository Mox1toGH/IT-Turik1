from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, RoleActivationCode
from backend.permissions import Permission, user_has_permission

class UserRoleTests(APITestCase):
    users_url = reverse('users')

    def test_tournament_permissions_match_role_responsibilities(self):
        admin = User.objects.create_user(
            username='permission-admin', email='permission-admin@example.com', password='StrongPass123!', role='admin', is_active=True,
        )
        organizer = User.objects.create_user(
            username='permission-organizer', email='permission-organizer@example.com', password='StrongPass123!', role='organizer', is_active=True,
        )
        jury = User.objects.create_user(
            username='permission-jury', email='permission-jury@example.com', password='StrongPass123!', role='jury', is_active=True,
        )
        self.assertTrue(user_has_permission(admin, Permission.CREATE_TOURNAMENT))
        self.assertTrue(user_has_permission(organizer, Permission.CREATE_TOURNAMENT))
        self.assertFalse(user_has_permission(jury, Permission.CREATE_TOURNAMENT))

    def test_create_superuser_uses_admin_role(self):
        user = User.objects.create_superuser(username='root', email='r@e.com', password='P')
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_superuser)

    def test_user_list_excludes_superusers(self):
        requester = User.objects.create_user(username='requester', email='req@e.com', password='P', role='team', is_active=True)
        User.objects.create_user(username='team-user', email='t@e.com', password='P', role='team', is_active=True)
        User.objects.create_user(username='super', email='s@e.com', password='P', role='team', is_active=True, is_superuser=True)
        self.client.force_authenticate(user=requester)
        response = self.client.get(self.users_url)
        usernames = [user['username'] for user in response.data]
        self.assertIn('team-user', usernames)
        self.assertNotIn('super', usernames)

class UserDetailViewTests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(username='detail-req', email='req@e.com', password='P', is_active=True)
        self.client.force_authenticate(user=self.requester)

    def test_authenticated_user_can_fetch_profile(self):
        target = User.objects.create_user(username='target', email='t@e.com', password='P', is_active=True)
        url = reverse('user_detail', kwargs={'pk': target.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_is_excluded_from_detail(self):
        superuser = User.objects.create_user(username='super', email='s@e.com', password='P', is_active=True, is_superuser=True)
        url = reverse('user_detail', kwargs={'pk': superuser.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_inactive_user_is_excluded_from_detail(self):
        inactive = User.objects.create_user(username='inactive', email='i@e.com', password='P', is_active=False)
        url = reverse('user_detail', kwargs={'pk': inactive.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class RoleRegistrationTests(APITestCase):
    register_url = reverse('register')
    role_codes_url = reverse('role_codes_admin')

    def test_team_member_registration_does_not_require_code(self):
        response = self.client.post(self.register_url, {'username': 'u', 'email': 'u@e.com', 'password': 'Pass123!', 'role': 'team'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_restricted_role_registration_requires_redeem_code(self):
        response = self.client.post(self.register_url, {'username': 'j', 'email': 'j@e.com', 'password': 'Pass123!', 'role': 'jury'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restricted_role_registration_consumes_code_once(self):
        code = RoleActivationCode.objects.create(code='CODE', role='jury')
        payload = {'username': 'j1', 'email': 'j1@e.com', 'password': 'Pass123!', 'role': 'jury', 'redeem_code': 'CODE'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.register_url, payload.update({'username': 'j2', 'email': 'j2@e.com'}) or payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_role_registration_elevates_to_superuser(self):
        RoleActivationCode.objects.create(code='ADMIN', role='admin')
        response = self.client.post(self.register_url, {'username': 'a', 'email': 'a@e.com', 'password': 'Pass123!', 'role': 'admin', 'redeem_code': 'ADMIN'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='a')
        self.assertTrue(user.is_superuser)

    def test_non_admin_cannot_manage_role_codes(self):
        user = User.objects.create_user(username='u', email='u@e.com', password='P')
        self.client.force_authenticate(user=user)
        response = self.client.get(self.role_codes_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
