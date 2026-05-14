from django.test import TestCase
from django.core.exceptions import ValidationError
from shop.models import Category, Product, Order, AvatarFrame
from accounts.models import User

class ShopModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test-user', email='test@example.com')
        self.category = Category.objects.create(name='Test Category')

    def test_product_str(self):
        product = Product.objects.create(
            name='Test Product',
            price=100,
            stock_quantity=10,
            category=self.category
        )
        self.assertEqual(str(product), 'Test Product')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

    def test_avatar_frame_str(self):
        frame = AvatarFrame.objects.create(name='Cool Frame', svg_file='path/to/svg')
        self.assertEqual(str(frame), 'Cool Frame')

    def test_order_str(self):
        product = Product.objects.create(name='P', price=10, stock_quantity=1, category=self.category)
        order = Order.objects.create(user=self.user, product=product, quantity=1, total_cost=10)
        self.assertEqual(str(order), f'Order {order.id} by {self.user.id}')

    def test_product_is_available_logic(self):
        # Testing logic that is used in serializer but based on model state
        def is_available(obj):
            if obj.product_type == Product.TYPE_DIGITAL:
                return bool(obj.is_active)
            return bool(obj.is_active and obj.stock_quantity > 0)

        product = Product.objects.create(name='P', price=10, stock_quantity=1, category=self.category, is_active=True)
        self.assertTrue(is_available(product))
        product.stock_quantity = 0
        self.assertFalse(is_available(product))
        product.stock_quantity = 10
        product.is_active = False
        self.assertFalse(is_available(product))

    def test_negative_price_validation(self):
        product = Product(name='P', price=-10, stock_quantity=1, category=self.category)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_negative_stock_validation(self):
        product = Product(name='P', price=10, stock_quantity=-1, category=self.category)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_order_total_cost_calculation(self):
        product = Product.objects.create(name='P', price=15, stock_quantity=10, category=self.category)
        order = Order.objects.create(user=self.user, product=product, quantity=3, total_cost=45)
        self.assertEqual(order.total_cost, 45)

    def test_digital_product_requires_avatar_frame_if_applicable(self):
        # This is more of a business logic check, if enforced in models
        # For now just testing we can create it
        frame = AvatarFrame.objects.create(name='F', svg_file='S')
        product = Product.objects.create(
            name='Digital', 
            price=10, 
            stock_quantity=1, 
            category=self.category,
            product_type=Product.TYPE_DIGITAL,
            avatar_frame=frame
        )
        self.assertEqual(product.avatar_frame, frame)

    def test_category_unique_name(self):
        with self.assertRaises(Exception): # IntegrityError
             Category.objects.create(name='Test Category')
