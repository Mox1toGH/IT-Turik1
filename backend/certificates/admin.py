from django.contrib import admin
from .models import CertificateTemplate, Certificate


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'created_at')
    list_filter = ('is_default',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'tournament', 'placement', 'unique_code', 'created_at')
    search_fields = ('user__full_name', 'user__username', 'tournament__name', 'unique_code')
