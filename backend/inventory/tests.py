from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from inventory.models import UserInventory
from points.models import UserPointsBalance
from shop.models import AvatarFrame, Category, Product


class InventoryApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='inventory-user',
            email='inventory-user@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.other_user = User.objects.create_user(
            username='inventory-other',
            email='inventory-other@example.com',
            password='StrongPass123!',
            role='team',
        )

        self.category = Category.objects.create(name=f'Inventory Digital Goods {self.user.username}')
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
        self.second_digital_product = Product.objects.create(
            name='Digital Border',
            description='Second digital item',
            price=25,
            stock_quantity=10,
            category=self.category,
            product_type=Product.TYPE_DIGITAL,
            avatar_frame=self.avatar_frame,
            is_active=True,
        )
        self.physical_product = Product.objects.create(
            name='Physical Mouse',
            description='Physical item',
            price=15,
            stock_quantity=5,
            category=self.category,
            product_type=Product.TYPE_PHYSICAL,
            is_active=True,
        )

        self.inventory_url = reverse('inventory-my')
        self.equip_url = reverse('inventory-equip')
        self.unequip_url = reverse('inventory-unequip')
        self.purchase_url = reverse('shop-purchase')

    def test_my_inventory_list_returns_only_current_user_items(self):
        UserInventory.objects.create(user=self.user, product=self.digital_product)
        UserInventory.objects.create(user=self.other_user, product=self.second_digital_product)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.inventory_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['product']['id'], self.digital_product.id)

    def test_equip_inventory_item_marks_selected_item_equipped_and_unsets_previous(self):
        first_item = UserInventory.objects.create(user=self.user, product=self.digital_product)
        second_item = UserInventory.objects.create(user=self.user, product=self.second_digital_product)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.equip_url, {'inventory_id': second_item.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_item.refresh_from_db()
        second_item.refresh_from_db()
        self.assertFalse(first_item.is_equipped)
        self.assertTrue(second_item.is_equipped)

    def test_equip_rejects_non_digital_items(self):
        inventory_item = UserInventory.objects.create(user=self.user, product=self.physical_product)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.equip_url, {'inventory_id': inventory_item.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['details']['inventory_id'],
            'Only digital items can be equipped.',
        )

    def test_unequip_inventory_item(self):
        inventory_item = UserInventory.objects.create(user=self.user, product=self.digital_product, is_equipped=True)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.unequip_url, {'inventory_id': inventory_item.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inventory_item.refresh_from_db()
        self.assertFalse(inventory_item.is_equipped)

    def test_purchase_digital_product_creates_inventory_item(self):
        UserPointsBalance.objects.create(user=self.user, balance=500)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.digital_product.id, 'quantity': 1},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserInventory.objects.filter(user=self.user, product=self.digital_product).exists()
        )

    def test_purchase_digital_product_rejects_duplicate_ownership(self):
        UserInventory.objects.create(user=self.user, product=self.digital_product)
        UserPointsBalance.objects.create(user=self.user, balance=500)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.purchase_url,
            {'product_id': self.digital_product.id, 'quantity': 1},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
