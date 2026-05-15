from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from accounts.models import User
from notifications.services import NotificationService
from .models import NewsArticle

from drf_spectacular.utils import extend_schema_field, inline_serializer
from drf_spectacular.types import OpenApiTypes

class NewsArticleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    send_notification = serializers.BooleanField(write_only=True, required=False, default=False)
    content = serializers.DictField(required=True)

    class Meta:
        model = NewsArticle
        fields = (
            'id',
            'title',
            'content',
            'created_by',
            'created_by_name',
            'send_notification',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_by', 'created_by_name', 'created_at', 'updated_at')

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return ''
        return obj.created_by.full_name or obj.created_by.username

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        send_notification = validated_data.pop('send_notification', False)
        article = NewsArticle(created_by=getattr(request, 'user', None), **validated_data)
        try:
            article.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        article.save()

        if send_notification:
            recipients = User.objects.exclude(id=getattr(request.user, 'id', None))
            NotificationService.notify(
                recipients=recipients,
                event_type='news_published',
                context={'news_id': article.id, 'news_title': article.title},
            )
        return article

    @transaction.atomic
    def update(self, instance, validated_data):
        send_notification = validated_data.pop('send_notification', False)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        instance.save()

        if send_notification:
            request = self.context.get('request')
            recipients = User.objects.exclude(id=getattr(request.user, 'id', None))
            NotificationService.notify(
                recipients=recipients,
                event_type='news_published',
                context={'news_id': instance.id, 'news_title': instance.title},
            )
        return instance
