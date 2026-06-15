from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'event_type', 'title', 'message', 'is_read', 'created_at')
        read_only_fields = fields

class DetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class MarkedCountResponseSerializer(serializers.Serializer):
    marked = serializers.IntegerField()


class UnreadCountResponseSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()


class DeletedCountResponseSerializer(serializers.Serializer):
    deleted = serializers.IntegerField()


class EventTypeSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()


class NotificationConfigSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    is_system_enabled = serializers.BooleanField()
    is_email_enabled = serializers.BooleanField()


class GlobalConfigSerializer(serializers.Serializer):
    emails_disabled_globally = serializers.BooleanField()


class NotificationSettingsResponseSerializer(serializers.Serializer):
    event_types = EventTypeSerializer(many=True)
    configs = NotificationConfigSerializer(many=True)
    global_config = GlobalConfigSerializer()


class NotificationConfigUpdateSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    is_system_enabled = serializers.BooleanField(required=False)
    is_email_enabled = serializers.BooleanField(required=False)


class GlobalConfigUpdateSerializer(serializers.Serializer):
    emails_disabled_globally = serializers.BooleanField()