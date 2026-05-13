from django.db import transaction

from .models import PointsTransaction, UserPointsBalance


@transaction.atomic
def apply_points_modification(*, user, operation, reason, amount=None):
    balance_obj, _ = UserPointsBalance.objects.select_for_update().get_or_create(
        user=user,
        defaults={'balance': 0},
    )

    current_balance = balance_obj.balance

    if operation == 'add':
        delta = int(amount)
        new_balance = current_balance + delta
    elif operation == 'subtract':
        delta = -int(amount)
        new_balance = current_balance + delta
    elif operation == 'set':
        new_balance = int(amount)
        delta = new_balance - current_balance
    elif operation == 'reset':
        new_balance = 0
        delta = -current_balance
    else:
        raise ValueError('Unsupported operation.')

    balance_obj.balance = new_balance
    balance_obj.save(update_fields=['balance', 'updated_at'])

    transaction_obj = PointsTransaction.objects.create(
        user=user,
        amount=delta,
        reason=reason,
    )

    return balance_obj, transaction_obj
