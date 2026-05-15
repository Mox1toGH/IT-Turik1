from django.conf import settings
from django.db import models


class UserPointsBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='points_balance',
    )
    balance = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id}: {self.balance}'


class PointsTransaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='points_transactions',
    )
    order = models.ForeignKey(
        'shop.Order',
        on_delete=models.SET_NULL,
        related_name='points_transactions',
        null=True,
        blank=True,
    )
    amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='points_txn_user_date_idx'),
            models.Index(fields=['user', 'amount'], name='points_txn_user_amount_idx'),
        ]

    def __str__(self):
        return f'{self.user_id}: {self.amount} ({self.reason})'
