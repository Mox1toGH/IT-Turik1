from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ninja import Query, Router
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from backend.auth import JWTAuth
from backend.permissions import is_platform_admin
from notifications.services import NotificationService

from .models import PointsTransaction, UserPointsBalance

from backend.schemas import ErrorResponse
from .schemas import ModifyPointsRequest, ModifyPointsResponse, PointsBalanceResponse, PointsTransactionResponse
from .services import apply_points_modification

User = get_user_model()
router = Router(tags=['points'], auth=JWTAuth())


def _require_admin(request):
    if not is_platform_admin(request.auth):
        raise HttpError(403, 'Only admins can manage points.')


def _ordered_transactions(queryset, ordering: str):
    if ordering not in {'created_at', '-created_at', 'amount', '-amount'}:
        raise HttpError(400, 'Unsupported ordering. Use created_at, -created_at, amount, or -amount.')
    return queryset.order_by(ordering, '-id')


def _balance(user):
    balance, _ = UserPointsBalance.objects.get_or_create(user=user, defaults={'balance': 0})
    return balance


@router.get('/my/balance', operation_id='getMyPointsBalance', response={200: PointsBalanceResponse, 401: ErrorResponse})
def get_my_balance(request):
    return PointsBalanceResponse.model_validate(
        _balance(request.auth),
        from_attributes=True,
    )


@router.get('/my/transactions', operation_id='listMyPointsTransactions', response={200: list[PointsTransactionResponse], 400: ErrorResponse, 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_my_transactions(request, ordering: str = '-created_at'):
    return _ordered_transactions(PointsTransaction.objects.filter(user=request.auth), ordering)


@router.get('/users/{user_id}/balance', operation_id='getAdminUserPointsBalance', response={200: PointsBalanceResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_user_balance(request, user_id: int):
    _require_admin(request)

    return PointsBalanceResponse.model_validate(
        _balance(get_object_or_404(User, pk=user_id)),
        from_attributes=True,
    )


@router.get('/users/{user_id}/transactions', operation_id='listAdminUserPointsTransactions', response={200: list[PointsTransactionResponse], 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_user_transactions(request, user_id: int, ordering: str = '-created_at'):
    _require_admin(request)
    user = get_object_or_404(User, pk=user_id)
    return _ordered_transactions(PointsTransaction.objects.filter(user=user), ordering)


@router.post('/users/{user_id}/balance', operation_id='modifyUserPointsBalance', response={200: ModifyPointsResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def modify_user_balance(request, user_id: int, payload: ModifyPointsRequest):
    _require_admin(request)
    
    user = get_object_or_404(User.objects.only('id', 'username', 'email'), pk=user_id)
    balance, transaction = apply_points_modification(
        user=user, operation=payload.operation, reason=payload.reason, amount=payload.amount,
    )

    NotificationService.notify(
        recipients=[user], event_type='points_balance_changed',
        context={'delta': transaction.amount, 'balance': balance.balance, 'reason': transaction.reason},
    )
    
    return ModifyPointsResponse(
        user=user,
        balance=balance,
        transaction=transaction,
    )
