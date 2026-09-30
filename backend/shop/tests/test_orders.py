from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from points.models import PointsTransaction, UserPointsBalance
from shop.models import Category, Order, Product, AvatarFrame
from inventory.models import UserInventory
from backend.auth import authenticate

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shop-user',
            email='shop-user@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.other_user = User.objects.create_user(
            username='shop-other',
            email='shop-other@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.category = Category.objects.create(name='Hardware')
        self.product = Product.objects.create(
            name='Keyboard',
            description='Mechanical keyboard',
            price=50,
            stock_quantity=10,
            category=self.category,
            product_type=Product.TYPE_PHYSICAL,
            is_active=True,
        )
        self.avatar_frame = AvatarFrame.objects.create(
            name=f'Inventory Frame {self.user.username}',
            svg_file='avatar-frames/inventory.svg',
            is_active=True,
        )
        self.digital_product = Product.objects.create(
            name='Digital Badge',
            description='Digital item',
            price=20,
            stock_quantity=10,
            category=self.category,
            product_type=Product.TYPE_DIGITAL,
            avatar_frame=self.avatar_frame,
            is_active=True,
        )
        self.purchase_url = reverse('ninja-api:shop-purchase')
        self.my_orders_url = reverse('ninja-api:shop-my-orders')

    def test_purchase_digital_product_rejects_duplicate_ownership(self):
            UserInventory.objects.create(user=self.user, product=self.digital_product)
            UserPointsBalance.objects.create(user=self.user, balance=500)
            authenticate(self.client, self.user)
    
            response = self.client.post(
                self.purchase_url,
                {'product_id': self.digital_product.id, 'quantity': 1},
                format='json',
            )
    
            data = response.json()

    
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                data,
                "product_id: You already own this digital item.",
            )
    
            self.assertEqual(
                UserInventory.objects.filter(
                    user=self.user,
                    product=self.digital_product,
                ).count(),
                1,
            )
            self.assertEqual(
                UserPointsBalance.objects.get(user=self.user).balance,
                500,
            )
    

    def test_purchase_success_creates_pending_order_deducts_points_stock_and_links_transaction(self):
        UserPointsBalance.objects.create(user=self.user, balance=200)
        authenticate(self.client, self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 2},
            format='json',
        )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=data['id'])
        self.product.refresh_from_db()
        balance = UserPointsBalance.objects.get(user=self.user)
        purchase_tx = PointsTransaction.objects.get(order=order)

        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.total_cost, 100)
        self.assertEqual(self.product.stock_quantity, 8)
        self.assertEqual(balance.balance, 100)
        self.assertEqual(purchase_tx.amount, -100)

    def test_purchase_rejects_when_insufficient_balance(self):
        UserPointsBalance.objects.create(user=self.user, balance=20)
        authenticate(self.client, self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_purchase_rejects_when_insufficient_stock(self):
        UserPointsBalance.objects.create(user=self.user, balance=999)
        authenticate(self.client, self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 50},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_user_can_cancel_only_own_order_and_get_refund_and_stock_return(self):
        UserPointsBalance.objects.create(user=self.user, balance=300)
        authenticate(self.client, self.user)
        purchase_response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 3},
            format='json',
        )
        purchase_response_data = purchase_response.json()
        order_id = purchase_response_data['id']

        cancel_url = reverse('ninja-api:shop-my-order-cancel', kwargs={'order_id': order_id})
        cancel_response = self.client.post(cancel_url, {}, format='json')
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=order_id)
        self.product.refresh_from_db()
        balance = UserPointsBalance.objects.get(user=self.user)

        self.assertEqual(order.status, Order.STATUS_CANCELLED)
        self.assertEqual(self.product.stock_quantity, 10)
        self.assertEqual(balance.balance, 300)

    def test_user_cannot_cancel_other_users_order(self):
        UserPointsBalance.objects.create(user=self.other_user, balance=300)
        authenticate(self.client, self.other_user)
        purchase_response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )
        purchase_response_data = purchase_response.json()
        order_id = purchase_response_data['id']

        authenticate(self.client, self.user)
        cancel_url = reverse('ninja-api:shop-my-order-cancel', kwargs={'order_id': order_id})
        response = self.client.post(cancel_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_order_history_returns_only_current_user_orders(self):
        UserPointsBalance.objects.create(user=self.user, balance=500)
        UserPointsBalance.objects.create(user=self.other_user, balance=500)

        authenticate(self.client, self.user)
        self.client.post(self.purchase_url, {'product_id': self.product.id, 'quantity': 1}, format='json')

        authenticate(self.client, self.other_user)
        self.client.post(self.purchase_url, {'product_id': self.product.id, 'quantity': 1}, format='json')

        authenticate(self.client, self.user)
        response = self.client.get(self.my_orders_url)

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 1)
