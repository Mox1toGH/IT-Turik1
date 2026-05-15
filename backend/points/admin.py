from django.contrib import admin

from .models import PointsTransaction, TournamentPointsAward, UserPointsBalance


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


from .models import TournamentPointsAward


@admin.register(TournamentPointsAward)
class TournamentPointsAwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tournament', 'team', 'award_type', 'rank', 'amount', 'created_at')
    search_fields = ('user__username', 'user__email', 'tournament__name', 'team__name')
    list_filter = ('award_type', 'created_at')
    list_select_related = ('user', 'tournament', 'team')
