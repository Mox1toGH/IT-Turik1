from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from points.models import PointsTransaction, UserPointsBalance

class PointsApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='points-user',
            email='points-user@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.other_user = User.objects.create_user(
            username='points-other',
            email='points-other@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.admin = User.objects.create_user(
            username='points-admin',
            email='points-admin@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )

        self.my_balance_url = reverse('points-my-balance')
        self.my_transactions_url = reverse('points-my-transactions')
        self.admin_balance_url = reverse('points-admin-user-balance', kwargs={'user_id': self.user.id})
        self.admin_transactions_url = reverse('points-admin-user-transactions', kwargs={'user_id': self.user.id})
        self.admin_modify_url = reverse('points-admin-user-modify', kwargs={'user_id': self.user.id})

    def _seed_transactions_for_user(self):
        PointsTransaction.objects.create(user=self.user, amount=30, reason='Bonus')
        PointsTransaction.objects.create(user=self.user, amount=-10, reason='Penalty')
        PointsTransaction.objects.create(user=self.user, amount=5, reason='Adjustment')

    def test_my_balance_requires_authentication(self):
        response = self.client.get(self.my_balance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_balance_returns_zero_if_missing(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.my_balance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 0)

    def test_my_transactions_returns_only_current_user_transactions(self):
        self.client.force_authenticate(user=self.user)
        PointsTransaction.objects.create(user=self.user, amount=15, reason='My tx')
        PointsTransaction.objects.create(user=self.other_user, amount=99, reason='Other tx')
        response = self.client.get(self.my_transactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_my_transactions_support_ordering_by_amount(self):
        self.client.force_authenticate(user=self.user)
        self._seed_transactions_for_user()
        response = self.client.get(self.my_transactions_url, {'ordering': 'amount'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        amounts = [item['amount'] for item in response.data['results']]
        self.assertEqual(amounts, sorted(amounts))

    def test_my_transactions_reject_invalid_ordering(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.my_transactions_url, {'ordering': 'created'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_transactions_support_pagination(self):
        self.client.force_authenticate(user=self.user)
        for index in range(3):
            PointsTransaction.objects.create(user=self.user, amount=index + 1, reason=f'Tx {index + 1}')
        response = self.client.get(self.my_transactions_url, {'page_size': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_admin_can_view_any_user_balance(self):
        UserPointsBalance.objects.create(user=self.user, balance=77)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.admin_balance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 77)

    def test_non_admin_cannot_view_admin_balance_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.admin_balance_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_any_user_transactions(self):
        self.client.force_authenticate(user=self.admin)
        self._seed_transactions_for_user()
        response = self.client.get(self.admin_transactions_url, {'ordering': '-amount'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_admin_modify_add_updates_balance(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.admin_modify_url, {'operation': 'add', 'amount': 25, 'reason': 'Bonus'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance']['balance'], 25)

    def test_admin_modify_subtract_updates_balance(self):
        self.client.force_authenticate(user=self.admin)
        UserPointsBalance.objects.create(user=self.user, balance=40)
        response = self.client.post(self.admin_modify_url, {'operation': 'subtract', 'amount': 12, 'reason': 'Penalty'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance']['balance'], 28)

    def test_admin_modify_set_updates_balance(self):
        self.client.force_authenticate(user=self.admin)
        UserPointsBalance.objects.create(user=self.user, balance=10)
        response = self.client.post(self.admin_modify_url, {'operation': 'set', 'amount': 50, 'reason': 'Set'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance']['balance'], 50)

    def test_admin_modify_reset_updates_balance(self):
        self.client.force_authenticate(user=self.admin)
        UserPointsBalance.objects.create(user=self.user, balance=19)
        response = self.client.post(self.admin_modify_url, {'operation': 'reset', 'reason': 'Reset'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance']['balance'], 0)

    def test_non_admin_cannot_modify_balance(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.admin_modify_url, {'operation': 'add', 'amount': 1, 'reason': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_modify_validation_requires_amount_for_add(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.admin_modify_url, {'operation': 'add', 'reason': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_modify_validation_rejects_amount_for_reset(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.admin_modify_url, {'operation': 'reset', 'amount': 3, 'reason': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
