from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import NewsArticle


class NewsArticleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = (
            'id',
            'title',
            'content',
            'created_by',
            'created_by_name',
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
        article = NewsArticle(created_by=getattr(request, 'user', None), **validated_data)
        try:
            article.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        article.save()
        return article

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        instance.save()
        return instance

