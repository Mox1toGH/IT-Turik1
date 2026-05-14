from django.contrib import admin
from .models import UserInventory


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'is_equipped', 'acquired_at')
    list_filter = ('is_equipped', 'acquired_at')
    search_fields = ('user__username', 'user__email', 'product__name')
    list_select_related = ('user', 'product')
