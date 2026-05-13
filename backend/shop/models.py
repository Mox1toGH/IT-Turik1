from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ['name', 'id']

    def __str__(self):
        return self.name


class AvatarFrame(models.Model):
    name = models.CharField(max_length=100, unique=True)
    svg_file = models.FileField(upload_to='avatar-frames/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'id']

    def __str__(self):
        return self.name


class Product(models.Model):
    TYPE_PHYSICAL = 'physical'
    TYPE_DIGITAL = 'digital'
    TYPE_CHOICES = (
        (TYPE_PHYSICAL, 'Physical'),
        (TYPE_DIGITAL, 'Digital'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(help_text='Price in points')
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    product_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_PHYSICAL)
    avatar_frame = models.ForeignKey(
        AvatarFrame,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        limit_choices_to={'is_active': True}
    )
    digital_asset_url = models.TextField(blank=True)  # deprecated, kept for backward compatibility
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'id']

    def __str__(self):
        return self.name

    @property
    def effective_digital_asset_url(self):
        """Get the digital asset URL, preferring avatar_frame.svg_file over digital_asset_url"""
        if self.avatar_frame and self.avatar_frame.svg_file:
            return self.avatar_frame.svg_file.url
        return self.digital_asset_url


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='shop/products/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPED = 'shipped'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop_orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quantity = models.PositiveIntegerField()
    total_cost = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='shop_order_user_date_idx'),
            models.Index(fields=['status', '-created_at'], name='shop_order_status_date_idx'),
        ]

    def __str__(self):
        return f'Order {self.id} by {self.user_id}'


