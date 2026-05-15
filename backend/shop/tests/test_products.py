from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from shop.models import Category, Product, AvatarFrame

class ProductTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shop-user',
            email='shop-user@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.category = Category.objects.create(name='Hardware')
        self.avatar_frame = AvatarFrame.objects.create(
            name='Test Frame',
            svg_file='avatar-frames/test.svg',
            is_active=True,
        )
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
            product_type=Product.TYPE_PHYSICAL,
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

    def test_product_detail_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product.id)
