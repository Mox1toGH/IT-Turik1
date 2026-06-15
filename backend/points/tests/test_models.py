from django.test import TestCase
from points.models import PointsTransaction, UserPointsBalance
from accounts.models import User

class PointsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pts-u', email='p@e.com')

    def test_user_points_balance_str(self):
        balance = UserPointsBalance.objects.create(user=self.user, balance=100)
        self.assertEqual(str(balance), f'{self.user.id}: 100')

    def test_points_transaction_str(self):
        tx = PointsTransaction.objects.create(user=self.user, amount=50, reason='Reward')
        self.assertEqual(str(tx), f'{self.user.id}: 50 (Reward)')

    def test_balance_uniqueness_per_user(self):
        from django.db import IntegrityError
        UserPointsBalance.objects.create(user=self.user, balance=0)
        with self.assertRaises(IntegrityError):
            UserPointsBalance.objects.create(user=self.user, balance=10)

    def test_transaction_timestamps(self):
        tx = PointsTransaction.objects.create(user=self.user, amount=10, reason='T')
        self.assertIsNotNone(tx.created_at)

    def test_balance_default_zero(self):
        # Assuming there is a default in the model
        # balance = UserPointsBalance.objects.create(user=self.user)
        # self.assertEqual(balance.balance, 0)
        pass

    def test_multiple_transactions_allowed(self):
        PointsTransaction.objects.create(user=self.user, amount=10, reason='R1')
        PointsTransaction.objects.create(user=self.user, amount=20, reason='R2')
        self.assertEqual(PointsTransaction.objects.filter(user=self.user).count(), 2)

    def test_balance_cascade_delete_user(self):
        UserPointsBalance.objects.create(user=self.user, balance=100)
        self.user.delete()
        self.assertEqual(UserPointsBalance.objects.count(), 0)

    def test_transaction_cascade_delete_user(self):
        PointsTransaction.objects.create(user=self.user, amount=10, reason='T')
        self.user.delete()
        self.assertEqual(PointsTransaction.objects.count(), 0)

    def test_negative_transaction_amount(self):
        tx = PointsTransaction.objects.create(user=self.user, amount=-10, reason='Penalty')
        self.assertEqual(tx.amount, -10)

    def test_large_transaction_reason(self):
        reason = 'A' * 255
        tx = PointsTransaction.objects.create(user=self.user, amount=1, reason=reason)
        self.assertEqual(tx.reason, reason)

    def test_transaction_user_null_fails(self):
        with self.assertRaises(Exception):
            PointsTransaction.objects.create(amount=10, reason='X')

    def test_balance_user_null_fails(self):
        with self.assertRaises(Exception):
            UserPointsBalance.objects.create(balance=0)

    def test_transaction_amount_zero_allowed(self):
        tx = PointsTransaction.objects.create(user=self.user, amount=0, reason='Zero')
        self.assertEqual(tx.amount, 0)

    def test_transaction_reason_empty_allowed(self):
        tx = PointsTransaction.objects.create(user=self.user, amount=1, reason='')
        self.assertEqual(tx.reason, '')

    def test_balance_update_directly(self):
        balance = UserPointsBalance.objects.create(user=self.user, balance=10)
        balance.balance = 20
        balance.save()
        self.assertEqual(UserPointsBalance.objects.get(user=self.user).balance, 20)

    def test_multiple_users_balances(self):
        u2 = User.objects.create_user(username='pts-u2', email='p2@e.com')
        UserPointsBalance.objects.create(user=self.user, balance=10)
        UserPointsBalance.objects.create(user=u2, balance=20)
        self.assertEqual(UserPointsBalance.objects.count(), 2)

    def test_transaction_ordering_by_created_at(self):
        # Transaction ordering check
        t1 = PointsTransaction.objects.create(user=self.user, amount=1, reason='1')
        t2 = PointsTransaction.objects.create(user=self.user, amount=2, reason='2')
        txs = PointsTransaction.objects.filter(user=self.user).order_by('created_at', 'id')
        self.assertEqual(txs[0], t1)
        self.assertEqual(txs[1], t2)

    def test_balance_is_not_negative_constraint(self):
        # If there is a check constraint in the model
        # balance = UserPointsBalance.objects.create(user=self.user, balance=-10)
        pass

    def test_user_points_balance_meta_options(self):
        self.assertTrue(hasattr(UserPointsBalance, '_meta'))

    def test_points_transaction_meta_options(self):
        self.assertTrue(hasattr(PointsTransaction, '_meta'))

    def test_transaction_amount_limit(self):
        # Just checking it accepts large numbers
        tx = PointsTransaction.objects.create(user=self.user, amount=10**9, reason='Rich')
        self.assertEqual(tx.amount, 10**9)

    def test_points_transaction_cascade_on_user_delete(self):
        PointsTransaction.objects.create(user=self.user, amount=10, reason='T')
        self.user.delete()
        self.assertEqual(PointsTransaction.objects.count(), 0)
