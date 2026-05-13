from django.db import transaction
from rest_framework.exceptions import ValidationError

from points.models import PointsTransaction, UserPointsBalance

from .models import Order, Product


@transaction.atomic
def create_order_purchase(*, user, product_id, quantity):
    product = Product.objects.select_for_update().select_related('category').get(pk=product_id, is_active=True)

    if product.product_type != Product.TYPE_PHYSICAL:
        raise ValidationError({'product_type': 'Only physical products can be purchased at the moment.'})

    if product.stock_quantity < quantity:
        raise ValidationError({'quantity': 'Not enough stock available.'})

    total_cost = product.price * quantity

    balance_obj, _ = UserPointsBalance.objects.select_for_update().get_or_create(
        user=user,
        defaults={'balance': 0},
    )

    if balance_obj.balance < total_cost:
        raise ValidationError({'balance': 'Insufficient points balance.'})

    order = Order.objects.create(
        user=user,
        product=product,
        quantity=quantity,
        total_cost=total_cost,
        status=Order.STATUS_PENDING,
    )

    balance_obj.balance -= total_cost
    balance_obj.save(update_fields=['balance', 'updated_at'])

    product.stock_quantity -= quantity
    product.save(update_fields=['stock_quantity', 'updated_at'])

    PointsTransaction.objects.create(
        user=user,
        amount=-total_cost,
        reason=f'Purchase order #{order.id}',
        order=order,
    )

    return order


@transaction.atomic
def cancel_order(*, order, cancelled_by):
    if order.status not in {Order.STATUS_PENDING, Order.STATUS_CONFIRMED}:
        raise ValidationError({'status': 'Only pending or confirmed orders can be cancelled.'})

    locked_order = Order.objects.select_for_update().select_related('product', 'user').get(pk=order.pk)
    if locked_order.status not in {Order.STATUS_PENDING, Order.STATUS_CONFIRMED}:
        raise ValidationError({'status': 'Only pending or confirmed orders can be cancelled.'})

    product = Product.objects.select_for_update().get(pk=locked_order.product_id)
    balance_obj, _ = UserPointsBalance.objects.select_for_update().get_or_create(
        user=locked_order.user,
        defaults={'balance': 0},
    )

    locked_order.status = Order.STATUS_CANCELLED
    locked_order.save(update_fields=['status', 'updated_at'])

    product.stock_quantity += locked_order.quantity
    product.save(update_fields=['stock_quantity', 'updated_at'])

    balance_obj.balance += locked_order.total_cost
    balance_obj.save(update_fields=['balance', 'updated_at'])

    PointsTransaction.objects.create(
        user=locked_order.user,
        amount=locked_order.total_cost,
        reason=f'Refund for order #{locked_order.id} cancelled by user #{cancelled_by.id}',
        order=locked_order,
    )

    return locked_order
