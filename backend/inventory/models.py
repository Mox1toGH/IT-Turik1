from django.conf import settings
from django.db import models
from shop.models import Product


class UserInventory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventory',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='owned_by_users',
        limit_choices_to={'product_type': Product.TYPE_DIGITAL},
    )
    is_equipped = models.BooleanField(default=False)
    acquired_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-acquired_at', '-id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='inventory_user_product_unique'),
        ]
        verbose_name_plural = 'User Inventories'

    def __str__(self):
        return f'User {self.user_id} owns Product {self.product_id}'
