from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from points.models import UserPointsBalance, PointsTransaction

class PointsApiAdvancedTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('pt_admin', 'p_a@e.com', 'pass', role='admin', is_staff=True)
        self.user1 = User.objects.create_user('pt_user1', 'p1@e.com', 'pass')
        self.user2 = User.objects.create_user('pt_user2', 'p2@e.com', 'pass')
        
        self.bal1 = UserPointsBalance.objects.create(user=self.user1, balance=500)
        self.bal2 = UserPointsBalance.objects.create(user=self.user2, balance=200)
        
        self.txn1 = PointsTransaction.objects.create(user=self.user1, amount=500, reason='Initial')
        self.txn2 = PointsTransaction.objects.create(user=self.user2, amount=200, reason='Initial')
        self.txn3 = PointsTransaction.objects.create(user=self.user1, amount=-100, reason='Purchase')
        
        self.bal1.balance -= 100
        self.bal1.save()

    # 15 tests
    def test_get_balance_unauthenticated(self):
        url = reverse('userpointsbalance-detail', kwargs={'pk': self.bal1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_balance_user1(self):
        url = reverse('userpointsbalance-detail', kwargs={'pk': self.bal1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 400)

    def test_get_balance_other_user_forbidden(self):
        url = reverse('userpointsbalance-detail', kwargs={'pk': self.bal1.id})
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_balances_admin(self):
        url = reverse('userpointsbalance-list')
        self.client.force_authenticate(self.admin)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_list_balances_user_sees_only_own(self):
        url = reverse('userpointsbalance-list')
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['balance'], 400)

    def test_list_transactions_unauthenticated(self):
        url = reverse('pointstransaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_transactions_user1(self):
        url = reverse('pointstransaction-list')
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_list_transactions_user2(self):
        url = reverse('pointstransaction-list')
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)

    def test_list_transactions_admin(self):
        url = reverse('pointstransaction-list')
        self.client.force_authenticate(self.admin)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 3)

    def test_retrieve_transaction_user1(self):
        url = reverse('pointstransaction-detail', kwargs={'pk': self.txn1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_transaction_other_user_forbidden(self):
        url = reverse('pointstransaction-detail', kwargs={'pk': self.txn1.id})
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_transaction_forbidden_for_user(self):
        url = reverse('pointstransaction-list')
        self.client.force_authenticate(self.user1)
        response = self.client.post(url, {'amount': 100, 'reason': 'Hack'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_transaction_forbidden_for_user(self):
        url = reverse('pointstransaction-detail', kwargs={'pk': self.txn1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.patch(url, {'amount': 999})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_transaction_forbidden_for_user(self):
        url = reverse('pointstransaction-detail', kwargs={'pk': self.txn1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_balance_forbidden_for_user(self):
        url = reverse('userpointsbalance-detail', kwargs={'pk': self.bal1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.patch(url, {'balance': 9999})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
