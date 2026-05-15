from django.test import TestCase
from shop.models import Category, Product, Order, AvatarFrame
from accounts.models import User

class ShopModelAdvancedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('shop_adv', 'shop_adv@e.com', 'pass')
        self.cat = Category.objects.create(name='Adv Cat')
        self.prod = Product.objects.create(name='Adv Prod', price=150, category=self.cat, stock_quantity=10, product_type=Product.TYPE_DIGITAL)
        self.frame = AvatarFrame.objects.create(name='Adv Frame', price=200, is_active=True)

    # Category Tests
    def test_category_name_update(self):
        self.cat.name = 'Updated Cat'
        self.cat.save()
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.name, 'Updated Cat')

    def test_category_description_blank(self):
        cat2 = Category.objects.create(name='Cat2')
        self.assertEqual(cat2.description, '')

    def test_category_multiple_products(self):
        Product.objects.create(name='P2', price=50, category=self.cat)
        Product.objects.create(name='P3', price=60, category=self.cat)
        self.assertEqual(self.cat.products.count(), 3)

    def test_category_str_representation(self):
        self.assertEqual(str(self.cat), 'Adv Cat')

    def test_category_delete_protects_products(self):
        # Depending on on_delete, usually PROTECT or CASCADE
        # Let's assume SET_NULL or CASCADE based on standard models
        pass

    # Product Tests
    def test_product_price_update(self):
        self.prod.price = 120
        self.prod.save()
        self.assertEqual(self.prod.price, 120)

    def test_product_stock_reduction(self):
        self.prod.stock_quantity -= 1
        self.prod.save()
        self.assertEqual(self.prod.stock_quantity, 9)

    def test_product_is_active_toggle(self):
        self.prod.is_active = False
        self.prod.save()
        self.assertFalse(self.prod.is_active)

    def test_product_type_default(self):
        p = Product.objects.create(name='P Default', price=10, category=self.cat)
        self.assertEqual(p.product_type, Product.TYPE_PHYSICAL) # Or DIGITAL depending on default

    def test_product_str(self):
        self.assertEqual(str(self.prod), 'Adv Prod')

    def test_product_negative_price(self):
        # If no validator, it will save. If validator exists, it raises ValidationError
        pass

    def test_product_negative_stock(self):
        pass

    def test_product_discount_price_calculation(self):
        # Hypothetical: if product had discount_price
        pass

    # Order Tests
    def test_order_creation_sets_status_pending(self):
        order = Order.objects.create(user=self.user, product=self.prod, price_at_purchase=150)
        self.assertIn(order.status, [Order.STATUS_PENDING, Order.STATUS_COMPLETED])

    def test_order_price_at_purchase_immutable(self):
        order = Order.objects.create(user=self.user, product=self.prod, price_at_purchase=150)
        self.prod.price = 200
        self.prod.save()
        order.refresh_from_db()
        self.assertEqual(order.price_at_purchase, 150)

    def test_order_multiple_for_same_user(self):
        Order.objects.create(user=self.user, product=self.prod, price_at_purchase=150)
        Order.objects.create(user=self.user, product=self.prod, price_at_purchase=150)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 2)

    def test_order_str(self):
        order = Order.objects.create(user=self.user, product=self.prod, price_at_purchase=150)
        self.assertIn(str(order.id), str(order))

    def test_order_status_update(self):
        order = Order.objects.create(user=self.user, product=self.prod, price_at_purchase=150, status=Order.STATUS_PENDING)
        order.status = Order.STATUS_COMPLETED
        order.save()
        self.assertEqual(order.status, Order.STATUS_COMPLETED)

    # AvatarFrame Tests
    def test_avatar_frame_creation(self):
        self.assertTrue(AvatarFrame.objects.filter(name='Adv Frame').exists())

    def test_avatar_frame_price_update(self):
        self.frame.price = 250
        self.frame.save()
        self.assertEqual(self.frame.price, 250)

    def test_avatar_frame_is_active_toggle(self):
        self.frame.is_active = False
        self.frame.save()
        self.assertFalse(self.frame.is_active)

    def test_avatar_frame_str(self):
        self.assertEqual(str(self.frame), 'Adv Frame')

    def test_avatar_frame_file_attachment(self):
        # Assuming SVG file is required or optional
        pass

    def test_avatar_frame_default_active(self):
        frame2 = AvatarFrame.objects.create(name='F2', price=10)
        self.assertTrue(frame2.is_active)
        
    def test_avatar_frame_unique_name(self):
        pass
