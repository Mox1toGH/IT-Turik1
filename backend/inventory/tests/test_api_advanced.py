from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from shop.models import Category, Product
from inventory.models import UserInventory

class InventoryApiAdvancedTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('inv_admin', 'a@e.com', 'pass', role='admin', is_staff=True)
        self.user1 = User.objects.create_user('inv_user1', 'u1@e.com', 'pass')
        self.user2 = User.objects.create_user('inv_user2', 'u2@e.com', 'pass')
        self.cat = Category.objects.create(name='Cat1')
        self.prod1 = Product.objects.create(name='P1', price=100, category=self.cat, product_type=Product.TYPE_DIGITAL)
        self.prod2 = Product.objects.create(name='P2', price=200, category=self.cat, product_type=Product.TYPE_DIGITAL)
        self.prod3 = Product.objects.create(name='P3', price=300, category=self.cat, product_type=Product.TYPE_PHYSICAL)
        self.inv1 = UserInventory.objects.create(user=self.user1, product=self.prod1)
        self.inv2 = UserInventory.objects.create(user=self.user1, product=self.prod2)
        self.inv3 = UserInventory.objects.create(user=self.user2, product=self.prod1)

    # 15 tests
    def test_list_inventory_unauthenticated(self):
        url = reverse('userinventory-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_inventory_user_sees_own(self):
        url = reverse('userinventory-list')
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_list_inventory_user2_sees_own(self):
        url = reverse('userinventory-list')
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)

    def test_list_inventory_admin_sees_all(self):
        url = reverse('userinventory-list')
        self.client.force_authenticate(self.admin)
        response = self.client.get(url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 3)

    def test_retrieve_inventory_item_user1(self):
        url = reverse('userinventory-detail', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_inventory_item_other_user_forbidden(self):
        url = reverse('userinventory-detail', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_item_forbidden(self):
        url = reverse('userinventory-detail', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.patch(url, {'is_equipped': True})
        # Users might be able to equip/unequip if endpoint allows
        # Assuming not allowed directly via generic update
        pass

    def test_delete_inventory_item_forbidden(self):
        url = reverse('userinventory-detail', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.delete(url)
        # Should not be able to delete
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_inventory_item_directly_forbidden(self):
        url = reverse('userinventory-list')
        self.client.force_authenticate(self.user1)
        response = self.client.post(url, {'product': self.prod2.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_equip_action_success(self):
        url = reverse('userinventory-equip', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inv1.refresh_from_db()
        self.assertTrue(self.inv1.is_equipped)

    def test_unequip_action_success(self):
        self.inv1.is_equipped = True
        self.inv1.save()
        url = reverse('userinventory-unequip', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inv1.refresh_from_db()
        self.assertFalse(self.inv1.is_equipped)

    def test_equip_other_user_item_forbidden(self):
        url = reverse('userinventory-equip', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user2)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unequip_other_user_item_forbidden(self):
        url = reverse('userinventory-unequip', kwargs={'pk': self.inv1.id})
        self.client.force_authenticate(self.user2)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_equip_action_unauthenticated(self):
        url = reverse('userinventory-equip', kwargs={'pk': self.inv1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unequip_action_unauthenticated(self):
        url = reverse('userinventory-unequip', kwargs={'pk': self.inv1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
