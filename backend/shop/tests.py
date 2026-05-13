from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from points.models import PointsTransaction, UserPointsBalance
from shop.models import Category, Order, Product, UserDigitalInventory


class ShopApiTests(APITestCase):
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

        self.products_url = reverse('shop-products-list')
        self.product_detail_url = reverse('shop-products-detail', kwargs={'pk': self.product.id})
        self.purchase_url = reverse('shop-purchase')
        self.my_orders_url = reverse('shop-my-orders')

    def test_product_list_requires_authentication(self):
        response = self.client.get(self.products_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_list_supports_filters_sort_and_marks_out_of_stock_as_unavailable(self):
        second_category = Category.objects.create(name='Digital')
        Product.objects.create(
            name='Mouse',
            description='Gaming mouse',
            price=30,
            stock_quantity=5,
            category=self.category,
            product_type=Product.TYPE_PHYSICAL,
            is_active=True,
        )
        Product.objects.create(
            name='Airdrop Code',
            description='Future digital item',
            price=10,
            stock_quantity=0,
            category=second_category,
            product_type=Product.TYPE_DIGITAL,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.products_url,
            {
                'search': 'o',
                'product_type': Product.TYPE_PHYSICAL,
                'category': self.category.id,
                'ordering': 'price',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'Mouse')
        self.assertEqual(results[1]['name'], 'Keyboard')

        out_of_stock_response = self.client.get(self.products_url, {'ordering': 'name'})
        self.assertEqual(out_of_stock_response.status_code, status.HTTP_200_OK)
        out_of_stock_item = [item for item in out_of_stock_response.data['results'] if item['name'] == 'Airdrop Code'][0]
        self.assertFalse(out_of_stock_item['is_available'])
        self.assertEqual(out_of_stock_response.data['results'][-1]['name'], 'Airdrop Code')

    def test_product_detail_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.product_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product.id)

    def test_purchase_success_creates_pending_order_deducts_points_stock_and_links_transaction(self):
        UserPointsBalance.objects.create(user=self.user, balance=200)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 2},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.product.refresh_from_db()
        balance = UserPointsBalance.objects.get(user=self.user)
        purchase_tx = PointsTransaction.objects.get(order=order)

        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.total_cost, 100)
        self.assertEqual(self.product.stock_quantity, 8)
        self.assertEqual(balance.balance, 100)
        self.assertEqual(purchase_tx.amount, -100)
        self.assertEqual(purchase_tx.user_id, self.user.id)

    def test_purchase_rejects_when_insufficient_balance(self):
        UserPointsBalance.objects.create(user=self.user, balance=20)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)

    def test_purchase_rejects_when_insufficient_stock(self):
        UserPointsBalance.objects.create(user=self.user, balance=999)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 50},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_purchase_digital_product_creates_inventory_item(self):
        digital = Product.objects.create(
            name='Digital Badge',
            description='Digital',
            price=5,
            stock_quantity=10,
            category=self.category,
            product_type=Product.TYPE_DIGITAL,
            digital_asset_url='/avatar-frames/fire-tongues.svg',
            is_active=True,
        )
        UserPointsBalance.objects.create(user=self.user, balance=500)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': digital.id, 'quantity': 1},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserDigitalInventory.objects.filter(user=self.user, product=digital).exists())

    def test_purchase_digital_product_rejects_duplicate_ownership(self):
        digital = Product.objects.create(
            name='Digital Border',
            description='Digital',
            price=8,
            stock_quantity=10,
            category=self.category,
            product_type=Product.TYPE_DIGITAL,
            digital_asset_url='/avatar-frames/fire-tongues.svg',
            is_active=True,
        )
        UserPointsBalance.objects.create(user=self.user, balance=500)
        UserDigitalInventory.objects.create(user=self.user, product=digital)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': digital.id, 'quantity': 1},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_inventory_and_equip(self):
        digital = Product.objects.create(
            name='Digital Flame',
            description='Digital',
            price=8,
            stock_quantity=10,
            category=self.category,
            product_type=Product.TYPE_DIGITAL,
            digital_asset_url='/avatar-frames/fire-tongues.svg',
            is_active=True,
        )
        inventory = UserDigitalInventory.objects.create(user=self.user, product=digital)
        self.client.force_authenticate(user=self.user)

        inventory_url = reverse('shop-my-inventory')
        equip_url = reverse('shop-inventory-equip')
        list_response = self.client.get(inventory_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)

        equip_response = self.client.post(equip_url, {'inventory_id': inventory.id}, format='json')
        self.assertEqual(equip_response.status_code, status.HTTP_200_OK)
        inventory.refresh_from_db()
        self.assertTrue(inventory.is_equipped)

    def test_user_can_cancel_only_own_order_and_get_refund_and_stock_return(self):
        UserPointsBalance.objects.create(user=self.user, balance=300)
        self.client.force_authenticate(user=self.user)
        purchase_response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 3},
            format='json',
        )
        order_id = purchase_response.data['id']

        cancel_url = reverse('shop-my-order-cancel', kwargs={'order_id': order_id})
        cancel_response = self.client.post(cancel_url, {}, format='json')

        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=order_id)
        self.product.refresh_from_db()
        balance = UserPointsBalance.objects.get(user=self.user)

        self.assertEqual(order.status, Order.STATUS_CANCELLED)
        self.assertEqual(self.product.stock_quantity, 10)
        self.assertEqual(balance.balance, 300)
        self.assertEqual(PointsTransaction.objects.filter(order=order).count(), 2)

    def test_user_cannot_cancel_other_users_order(self):
        UserPointsBalance.objects.create(user=self.other_user, balance=300)
        self.client.force_authenticate(user=self.other_user)
        purchase_response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )
        order_id = purchase_response.data['id']

        self.client.force_authenticate(user=self.user)
        cancel_url = reverse('shop-my-order-cancel', kwargs={'order_id': order_id})
        response = self.client.post(cancel_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_rejects_when_order_not_pending_or_confirmed(self):
        UserPointsBalance.objects.create(user=self.user, balance=300)
        self.client.force_authenticate(user=self.user)
        purchase_response = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )
        order = Order.objects.get(id=purchase_response.data['id'])
        order.status = Order.STATUS_SHIPPED
        order.save(update_fields=['status', 'updated_at'])

        cancel_url = reverse('shop-my-order-cancel', kwargs={'order_id': order.id})
        response = self.client.post(cancel_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_SHIPPED)

    def test_my_order_history_returns_only_current_user_orders(self):
        UserPointsBalance.objects.create(user=self.user, balance=500)
        UserPointsBalance.objects.create(user=self.other_user, balance=500)

        self.client.force_authenticate(user=self.user)
        self.client.post(self.purchase_url, {'product_id': self.product.id, 'quantity': 1}, format='json')

        self.client.force_authenticate(user=self.other_user)
        self.client.post(self.purchase_url, {'product_id': self.product.id, 'quantity': 1}, format='json')

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.my_orders_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['user']['id'], self.user.id)

    def test_admin_can_crud_category_and_product(self):
        self.client.force_authenticate(user=self.admin)

        categories_url = reverse('shop-admin-categories-list-create')
        create_category = self.client.post(
            categories_url,
            {'name': 'Accessories'},
            format='json',
        )
        self.assertEqual(create_category.status_code, status.HTTP_201_CREATED)
        new_category_id = create_category.data['id']

        category_detail_url = reverse('shop-admin-categories-detail', kwargs={'pk': new_category_id})
        patch_category = self.client.patch(
            category_detail_url,
            {'name': 'Accessories Updated'},
            format='json',
        )
        self.assertEqual(patch_category.status_code, status.HTTP_200_OK)

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
            format='json',
        )
        self.assertEqual(create_product.status_code, status.HTTP_201_CREATED)
        new_product_id = create_product.data['id']

        product_detail_url = reverse('shop-admin-products-detail', kwargs={'pk': new_product_id})
        patch_product = self.client.patch(product_detail_url, {'price': 80}, format='json')
        self.assertEqual(patch_product.status_code, status.HTTP_200_OK)

        delete_product = self.client.delete(product_detail_url)
        self.assertEqual(delete_product.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_create_digital_product_with_asset_url(self):
        self.client.force_authenticate(user=self.admin)
        digital_category = Category.objects.create(name='Digital Goods')

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
                'digital_asset_url': '/avatar-frames/aurora-pulse.svg',
                'is_active': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['digital_asset_url'], '/avatar-frames/aurora-pulse.svg')
        self.assertEqual(response.data['product_type'], Product.TYPE_DIGITAL)

    def test_non_admin_cannot_access_admin_shop_endpoints(self):
        self.client.force_authenticate(user=self.user)

        admin_categories_url = reverse('shop-admin-categories-list-create')
        response = self.client.get(admin_categories_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_orders_filter_change_status_and_cancel(self):
        UserPointsBalance.objects.create(user=self.user, balance=500)
        self.client.force_authenticate(user=self.user)
        purchase = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )
        order_id = purchase.data['id']

        self.client.force_authenticate(user=self.admin)
        list_url = reverse('shop-admin-orders-list')
        list_response = self.client.get(list_url, {'status': Order.STATUS_PENDING, 'user': self.user.id})

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)
        self.assertIn(f'/api/accounts/users/{self.user.id}/', list_response.data['results'][0]['user_profile_url'])

        update_status_url = reverse('shop-admin-orders-status', kwargs={'order_id': order_id})
        update_response = self.client.patch(
            update_status_url,
            {'status': Order.STATUS_CONFIRMED},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        cancel_url = reverse('shop-admin-orders-cancel', kwargs={'order_id': order_id})
        cancel_response = self.client.post(cancel_url, {}, format='json')
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)

        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, Order.STATUS_CANCELLED)

    def test_admin_status_update_rejects_cancelled_status(self):
        UserPointsBalance.objects.create(user=self.user, balance=500)
        self.client.force_authenticate(user=self.user)
        purchase = self.client.post(
            self.purchase_url,
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )

        self.client.force_authenticate(user=self.admin)
        update_status_url = reverse('shop-admin-orders-status', kwargs={'order_id': purchase.data['id']})
        response = self.client.patch(
            update_status_url,
            {'status': Order.STATUS_CANCELLED},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
