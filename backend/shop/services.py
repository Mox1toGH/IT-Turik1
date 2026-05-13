from django.db import transaction
from rest_framework.exceptions import ValidationError

from points.models import PointsTransaction, UserPointsBalance

from inventory.models import UserInventory
from .models import Order, Product


@transaction.atomic
def create_order_purchase(*, user, product_id, quantity):
    product = Product.objects.select_for_update().select_related('category').get(pk=product_id, is_active=True)
    if product.product_type == Product.TYPE_DIGITAL:
        if quantity != 1:
            raise ValidationError({'quantity': 'Digital items can only be purchased in quantity of 1.'})
        if UserInventory.objects.filter(user=user, product=product).exists():
            raise ValidationError({'product_id': 'You already own this digital item.'})
    elif product.stock_quantity < quantity:
        raise ValidationError({'quantity': 'Not enough stock available.'})

    total_cost = product.price * quantity

    balance_obj, _ = UserPointsBalance.objects.select_for_update().get_or_create(
        user=user,
        defaults={'balance': 0},
    )

    if balance_obj.balance < total_cost:
        raise ValidationError({'balance': 'Insufficient points balance.'})

    order = None
    if product.product_type == Product.TYPE_PHYSICAL:
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            total_cost=total_cost,
            status=Order.STATUS_PENDING,
        )

    balance_obj.balance -= total_cost
    balance_obj.save(update_fields=['balance', 'updated_at'])

    if product.product_type == Product.TYPE_PHYSICAL:
        product.stock_quantity -= quantity
        product.save(update_fields=['stock_quantity', 'updated_at'])
    else:
        UserInventory.objects.create(user=user, product=product)

    PointsTransaction.objects.create(
        user=user,
        amount=-total_cost,
        reason=f'Purchase of {product.name}' if not order else f'Purchase order #{order.id}',
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

    if product.product_type == Product.TYPE_PHYSICAL:
        product.stock_quantity += locked_order.quantity
        product.save(update_fields=['stock_quantity', 'updated_at'])
    else:
        inventory_item = UserInventory.objects.filter(
            user=locked_order.user,
            product=product,
        ).first()
        if inventory_item is not None:
            inventory_item.delete()

    balance_obj.balance += locked_order.total_cost
    balance_obj.save(update_fields=['balance', 'updated_at'])

    PointsTransaction.objects.create(
        user=locked_order.user,
        amount=locked_order.total_cost,
        reason=f'Refund for order #{locked_order.id} cancelled by user #{cancelled_by.id}',
        order=locked_order,
    )

    return locked_order
