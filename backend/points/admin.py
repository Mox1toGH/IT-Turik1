from django.contrib import admin

from .models import PointsTransaction, UserPointsBalance


@admin.register(UserPointsBalance)
class UserPointsBalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'updated_at')
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'amount', 'reason', 'created_at')
    search_fields = ('user__username', 'user__email', 'reason')
    list_filter = ('created_at',)
    list_select_related = ('user', 'order')
