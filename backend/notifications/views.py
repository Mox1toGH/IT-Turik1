from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.openapi import _400, _401, _404

from .models import Notification, NotificationConfig, UserNotificationSettings
from .serializers import NotificationSerializer
from .config import EVENTS

from .serializers import (
    NotificationSerializer,
    DetailResponseSerializer,
    MarkedCountResponseSerializer,
    UnreadCountResponseSerializer,
    DeletedCountResponseSerializer,
    NotificationSettingsResponseSerializer,
    NotificationConfigUpdateSerializer,
    GlobalConfigUpdateSerializer,
)


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    operation_id='listNotifications',
    responses={
        200: NotificationSerializer(many=True),
        401: _401,
    },
)
class NotificationListView(generics.ListAPIView):
    """List current user's notifications, newest first."""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        cutoff_date = timezone.now() - timedelta(days=30)
        Notification.objects.filter(recipient=self.request.user, created_at__lt=cutoff_date).delete()
        return Notification.objects.filter(recipient=self.request.user)


@extend_schema(
    operation_id='markNotificationRead',
    request=None,
    responses={
        200: DetailResponseSerializer,
        401: _401,
        404: _404,
    },
)
class NotificationMarkReadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DetailResponseSerializer

    def post(self, request, pk):
        updated = Notification.objects.filter(
            id=pk, recipient=request.user, is_read=False,
        ).update(is_read=True)

        if updated == 0:
            return Response(
                DetailResponseSerializer({'detail': 'Notification not found or already read.'}).data,
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(DetailResponseSerializer({'detail': 'Marked as read.'}).data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='markAllNotificationsRead',
    request=None,
    responses={
        200: MarkedCountResponseSerializer,
        401: _401,
    },
)
class NotificationMarkAllReadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MarkedCountResponseSerializer

    def post(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response(MarkedCountResponseSerializer({'marked': count}).data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='getUnreadNotificationCount',
    request=None,
    responses={
        200: UnreadCountResponseSerializer,
        401: _401,
    },
)
class UnreadCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnreadCountResponseSerializer

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response(UnreadCountResponseSerializer({'unread_count': count}).data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='deleteNotification',
    request=None,
    responses={
        204: OpenApiResponse(description='Notification deleted successfully.'),
        401: _401,
        404: _404,
    },
)
class NotificationDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DetailResponseSerializer

    def delete(self, request, pk):
        deleted_count, _ = Notification.objects.filter(id=pk, recipient=request.user).delete()
        if deleted_count == 0:
            return Response(
                DetailResponseSerializer({'detail': 'Notification not found.'}).data,
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    operation_id='deleteAllNotifications',
    request=None,
    responses={
        200: DeletedCountResponseSerializer,
        401: _401,
    },
)
class NotificationDeleteAllView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeletedCountResponseSerializer

    def delete(self, request):
        deleted_count, _ = Notification.objects.filter(recipient=request.user).delete()
        return Response(DeletedCountResponseSerializer({'deleted': deleted_count}).data, status=status.HTTP_200_OK)


@extend_schema(methods=['GET'], operation_id='getNotificationSettings', responses={
    200: NotificationSettingsResponseSerializer,
    401: _401,
})
@extend_schema(methods=['PUT'], operation_id='updateNotificationSettings', responses={
    200: NotificationSettingsResponseSerializer,
    400: _400,
    401: _401,
})
class NotificationSettingsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSettingsResponseSerializer

    def get(self, request):
        user = request.user
        for key in EVENTS:
            NotificationConfig.objects.get_or_create(
                user=user,
                event_type=key,
                defaults={
                    'is_system_enabled': 'system' in EVENTS[key].channels,
                    'is_email_enabled': 'email' in EVENTS[key].channels,
                }
            )
        db_configs = NotificationConfig.objects.filter(user=user).values(
            'event_type', 'is_system_enabled', 'is_email_enabled'
        )
        user_settings, _ = UserNotificationSettings.objects.get_or_create(user=user)
        return Response(
            NotificationSettingsResponseSerializer({
                'event_types': [{'key': e.key, 'title': e.title_tpl} for e in EVENTS.values()],
                'configs': list(db_configs),
                'global_config': {'emails_disabled_globally': user_settings.emails_disabled_globally},
            }).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='updateNotificationConfig',
    request=NotificationConfigUpdateSerializer,
    responses={
        200: DetailResponseSerializer,
        400: _400,
        401: _401,
        404: _404,
    },
)
class NotificationConfigUpdateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationConfigUpdateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_type = serializer.validated_data['event_type']
        is_system = serializer.validated_data.get('is_system_enabled')
        is_email = serializer.validated_data.get('is_email_enabled')

        config = get_object_or_404(NotificationConfig, user=request.user, event_type=event_type)
        if is_system is not None:
            config.is_system_enabled = is_system
        if is_email is not None:
            config.is_email_enabled = is_email
        config.save()

        return Response(DetailResponseSerializer({'detail': f'Setting updated for {event_type}'}).data)


@extend_schema(
    operation_id='updateGlobalNotificationConfig',
    request=GlobalConfigUpdateSerializer,
    responses={
        200: DetailResponseSerializer,
        400: _400,
        401: _401,
    },
)
class GlobalConfigUpdateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GlobalConfigUpdateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        disabled = serializer.validated_data.get('emails_disabled_globally')

        user_settings, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
        if disabled is not None:
            user_settings.emails_disabled_globally = disabled
            user_settings.save()

        return Response(DetailResponseSerializer({'detail': 'Personal global email setting updated'}).data)