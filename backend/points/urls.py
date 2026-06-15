from django.urls import path

from .views import (
    AdminModifyUserPointsBalanceView,
    AdminUserPointsBalanceView,
    AdminUserPointsTransactionHistoryView,
    MyPointsBalanceView,
    MyPointsTransactionHistoryView,
)

urlpatterns = [
    path('balance/', MyPointsBalanceView.as_view(), name='points-my-balance'),
    path('transactions/', MyPointsTransactionHistoryView.as_view(), name='points-my-transactions'),

    path('admin/users/<int:user_id>/balance/', AdminUserPointsBalanceView.as_view(), name='points-admin-user-balance'),
    path('admin/users/<int:user_id>/transactions/', AdminUserPointsTransactionHistoryView.as_view(), name='points-admin-user-transactions'),
    path('admin/users/<int:user_id>/modify/', AdminModifyUserPointsBalanceView.as_view(), name='points-admin-user-modify'),
]
