import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.pagination import PageNumberPagination, paginate

from backend.auth import JWTAuth
from backend.permissions import is_platform_admin
from notifications.services import NotificationService

from .models import PointsTransaction, UserPointsBalance

from backend.schemas import ErrorResponse
from backend.errors import raise_api_error
from http import HTTPStatus
from .schemas import ModifyPointsRequest, ModifyPointsResponse, PointsBalanceResponse, PointsTransactionResponse
from .services import apply_points_modification

logger = logging.getLogger(__name__)

User = get_user_model()
router = Router(tags=['points'], auth=JWTAuth())


def _require_admin(request):
    if not is_platform_admin(request.auth):
        logger.warning(
            'Points admin access denied',
            extra={'user_id': request.auth.id, 'request_path': request.path},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only admins can manage points.')


def _ordered_transactions(queryset, ordering: str):
    if ordering not in {'created_at', '-created_at', 'amount', '-amount'}:
        logger.warning('Unsupported transaction ordering', extra={'ordering': ordering})
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Unsupported ordering. Use created_at, -created_at, amount, or -amount.')
    return queryset.order_by(ordering, '-id')


def _balance(user):
    balance, created = UserPointsBalance.objects.get_or_create(user=user, defaults={'balance': 0})
    if created:
        logger.info('Points balance initialised', extra={'user_id': user.id})
    return balance


@router.get('/my/balance', operation_id='getMyPointsBalance', url_name="points-my-balance", response={200: PointsBalanceResponse, 401: ErrorResponse})
def get_my_balance(request):
    logger.debug('Fetching own points balance', extra={'user_id': request.auth.id})
    return PointsBalanceResponse.model_validate(
        _balance(request.auth),
        from_attributes=True,
    )


@router.get('/my/transactions', operation_id='listMyPointsTransactions', url_name="points-my-transactions", response={200: list[PointsTransactionResponse], 400: ErrorResponse, 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_my_transactions(request, ordering: str = '-created_at'):
    logger.debug(
        'Listing own points transactions',
        extra={'user_id': request.auth.id, 'ordering': ordering},
    )
    return _ordered_transactions(PointsTransaction.objects.filter(user=request.auth), ordering)


@router.get('/users/{user_id}/balance', operation_id='getAdminUserPointsBalance', url_name="points-admin-user-balance", response={200: PointsBalanceResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_user_balance(request, user_id: int):
    _require_admin(request)
    logger.debug(
        'Admin fetching points balance',
        extra={'target_user_id': user_id, 'user_id': request.auth.id},
    )

    return PointsBalanceResponse.model_validate(
        _balance(get_object_or_404(User, pk=user_id)),
        from_attributes=True,
    )


@router.get('/users/{user_id}/transactions', operation_id='listAdminUserPointsTransactions', url_name="points-admin-user-transactions", response={200: list[PointsTransactionResponse], 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@paginate(PageNumberPagination, page_size=20)
def list_user_transactions(request, user_id: int, ordering: str = '-created_at'):
    _require_admin(request)
    logger.debug(
        'Admin listing points transactions',
        extra={
            'target_user_id': user_id,
            'user_id': request.auth.id,
            'ordering': ordering,
        },
    )
    user = get_object_or_404(User, pk=user_id)
    return _ordered_transactions(PointsTransaction.objects.filter(user=user), ordering)


@router.post('/users/{user_id}/balance', operation_id='modifyUserPointsBalance', url_name='points-admin-user-modify', response={200: ModifyPointsResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def modify_user_balance(request, user_id: int, payload: ModifyPointsRequest):
    _require_admin(request)
    logger.info(
        'Modifying points balance',
        extra={
            'target_user_id': user_id,
            'user_id': request.auth.id,
            'operation': payload.operation,
            'amount': payload.amount,
        },
    )

    user = get_object_or_404(User.objects.only('id', 'username', 'email'), pk=user_id)
    try:
        balance, transaction = apply_points_modification(
            user=user, operation=payload.operation, reason=payload.reason, amount=payload.amount,
        )
    except Exception:
        logger.exception(
            'Points modification failed',
            extra={
                'target_user_id': user_id,
                'user_id': request.auth.id,
                'operation': payload.operation,
                'amount': payload.amount,
            },
        )
        raise
    logger.info(
        'Points balance modified',
        extra={
            'transaction_id': transaction.id,
            'target_user_id': user_id,
            'user_id': request.auth.id,
            'delta': transaction.amount,
            'new_balance': balance.balance,
        },
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