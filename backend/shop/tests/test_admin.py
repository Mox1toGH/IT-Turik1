from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from points.models import UserPointsBalance
from shop.models import Category, Order, Product, AvatarFrame

class ShopAdminTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shop-user',
            email='shop-user@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.admin = User.objects.create_user(
            username='shop-admin',
            email='shop-admin@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
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
            name='Test Frame',
            svg_file='avatar-frames/test.svg',
            is_active=True,
        )
        self.purchase_url = reverse('shop-purchase')

    def test_admin_can_crud_category_and_product(self):
        self.client.force_authenticate(user=self.admin)

        categories_url = reverse('shop-admin-categories-list-create')
        create_category = self.client.post(categories_url, {'name': 'Accessories'}, format='json')
        self.assertEqual(create_category.status_code, status.HTTP_201_CREATED)
        new_category_id = create_category.data['id']

        products_url = reverse('shop-admin-products-list-create')
        create_product = self.client.post(
            products_url,
            {
                'name': 'Headset',
                'description': 'Wireless',
                'price': 70,
                'stock_quantity': 4,
                'category_id': new_category_id,
                'product_type': Product.TYPE_PHYSICAL,
                'is_active': True,
            },
        )
        self.assertEqual(create_product.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_digital_product_with_asset_url(self):
        self.client.force_authenticate(user=self.admin)
        digital_category, _ = Category.objects.get_or_create(name='Digital Goods')

        products_url = reverse('shop-admin-products-list-create')
        response = self.client.post(
            products_url,
            {
                'name': 'Animated Avatar Frame',
                'description': 'Animated profile frame asset',
                'price': 120,
                'stock_quantity': 1,
                'category_id': digital_category.id,
                'product_type': Product.TYPE_DIGITAL,
                'avatar_frame_id': self.avatar_frame.id,
                'is_active': True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cannot_access_admin_shop_endpoints(self):
        self.client.force_authenticate(user=self.user)
        admin_categories_url = reverse('shop-admin-categories-list-create')
        response = self.client.get(admin_categories_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_orders_filter_change_status_and_cancel(self):
        UserPointsBalance.objects.create(user=self.user, balance=500)
        self.client.force_authenticate(user=self.user)
        purchase = self.client.post(self.purchase_url, {'product_id': self.product.id, 'quantity': 1}, format='json')
        order_id = purchase.data['id']

        self.client.force_authenticate(user=self.admin)
        update_status_url = reverse('shop-admin-orders-status', kwargs={'order_id': order_id})
        update_response = self.client.patch(update_status_url, {'status': Order.STATUS_CONFIRMED}, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        cancel_url = reverse('shop-admin-orders-cancel', kwargs={'order_id': order_id})
        cancel_response = self.client.post(cancel_url, {}, format='json')
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_access_admin_orders(self):
        url = reverse('shop-admin-orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_user_cannot_update_order_status(self):
        UserPointsBalance.objects.create(user=self.user, balance=500)
        self.client.force_authenticate(user=self.user)
        purchase = self.client.post(self.purchase_url, {'product_id': self.product.id, 'quantity': 1}, format='json')
        order_id = purchase.data['id']

        update_status_url = reverse('shop-admin-orders-status', kwargs={'order_id': order_id})
        response = self.client.patch(update_status_url, {'status': Order.STATUS_CONFIRMED}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
