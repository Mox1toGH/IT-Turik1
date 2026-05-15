from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from backend.permissions import is_platform_admin

from .models import PointsTransaction, UserPointsBalance
from .serializers import (
    AdminPointsBalanceModifySerializer,
    PointsTransactionSerializer,
    UserPointsBalanceSerializer,
    UserLookupSerializer,
)
from .services import apply_points_modification

User = get_user_model()


class PointsTransactionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class _PointsHistoryBaseView(generics.ListAPIView):
    serializer_class = PointsTransactionSerializer
    pagination_class = PointsTransactionPagination

    def _ordered_queryset(self, queryset):
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed = {'created_at', '-created_at', 'amount', '-amount'}
        if ordering not in allowed:
            raise ValidationError({'ordering': 'Unsupported ordering. Use created_at, -created_at, amount, or -amount.'})
        return queryset.order_by(ordering, '-id')


class MyPointsBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        balance_obj, _ = UserPointsBalance.objects.get_or_create(
            user=request.user,
            defaults={'balance': 0},
        )
        data = {
            'user_id': request.user.id,
            'balance': balance_obj.balance,
            'updated_at': balance_obj.updated_at,
        }
        return Response(UserPointsBalanceSerializer(data).data)


class MyPointsTransactionHistoryView(_PointsHistoryBaseView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PointsTransaction.objects.filter(user=self.request.user)
        return self._ordered_queryset(queryset)


class AdminUserPointsBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if not is_platform_admin(request.user):
            raise PermissionDenied('Only admins can view user points balance.')

        target_user = get_object_or_404(User.objects.only('id'), pk=user_id)
        balance_obj, _ = UserPointsBalance.objects.get_or_create(
            user=target_user,
            defaults={'balance': 0},
        )
        data = {
            'user_id': target_user.id,
            'balance': balance_obj.balance,
            'updated_at': balance_obj.updated_at,
        }
        return Response(UserPointsBalanceSerializer(data).data)


class AdminUserPointsTransactionHistoryView(_PointsHistoryBaseView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not is_platform_admin(self.request.user):
            raise PermissionDenied('Only admins can view user transaction history.')

        target_user = get_object_or_404(User.objects.only('id'), pk=self.kwargs['user_id'])
        queryset = PointsTransaction.objects.filter(user=target_user)
        return self._ordered_queryset(queryset)


class AdminModifyUserPointsBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not is_platform_admin(request.user):
            raise PermissionDenied('Only admins can modify user points balance.')

        target_user = get_object_or_404(User.objects.only('id', 'username', 'email'), pk=user_id)

        serializer = AdminPointsBalanceModifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        balance_obj, transaction_obj = apply_points_modification(
            user=target_user,
            operation=payload['operation'],
            reason=payload['reason'],
            amount=payload.get('amount'),
        )

        response_data = {
            'user': UserLookupSerializer(target_user).data,
            'balance': UserPointsBalanceSerializer(
                {
                    'user_id': target_user.id,
                    'balance': balance_obj.balance,
                    'updated_at': balance_obj.updated_at,
                }
            ).data,
            'transaction': PointsTransactionSerializer(
                {
                    'id': transaction_obj.id,
                    'user_id': target_user.id,
                    'amount': transaction_obj.amount,
                    'reason': transaction_obj.reason,
                    'created_at': transaction_obj.created_at,
                }
            ).data,
        }
        return Response(response_data)
