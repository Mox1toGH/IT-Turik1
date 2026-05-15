from django.contrib import admin

from .models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'created_at', 'updated_at')
    search_fields = ('title', 'created_by__username', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')

