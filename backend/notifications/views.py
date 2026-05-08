from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, NotificationConfig, UserNotificationSettings
from .serializers import NotificationSerializer
from .config import EVENTS


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(generics.ListAPIView):
    """List current user's notifications, newest first."""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        cutoff_date = timezone.now() - timedelta(days=30)
        # Auto-delete notifications older than 30 days for this user
        Notification.objects.filter(recipient=self.request.user, created_at__lt=cutoff_date).delete()

        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadView(APIView):
    """Mark a single notification as read."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        updated = Notification.objects.filter(
            id=pk,
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)

        if updated == 0:
            return Response(
                {'detail': 'Notification not found or already read.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'detail': 'Marked as read.'}, status=status.HTTP_200_OK)


class NotificationMarkAllReadView(APIView):
    """Mark all unread notifications as read for the current user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)
        return Response({'marked': count}, status=status.HTTP_200_OK)


class UnreadCountView(APIView):
    """Return the number of unread notifications (for badge display)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)


class NotificationDeleteView(APIView):
    """Delete a single notification for the current user."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        deleted_count, _ = Notification.objects.filter(
            id=pk,
            recipient=request.user,
        ).delete()
        if deleted_count == 0:
            return Response({'detail': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationDeleteAllView(APIView):
    """Delete all notifications for the current user."""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        deleted_count, _ = Notification.objects.filter(recipient=request.user).delete()
        return Response({'deleted': deleted_count}, status=status.HTTP_200_OK)


class NotificationSettingsView(APIView):
    """Returns available event types and personal DB configs for the current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Ensure all events have a personal DB config for this user
        for key in EVENTS:
            NotificationConfig.objects.get_or_create(
                user=user,
                event_type=key,
                defaults={
                    'is_system_enabled': 'system' in EVENTS[key].channels,
                    'is_email_enabled': 'email' in EVENTS[key].channels
                }
            )

        db_configs = NotificationConfig.objects.filter(user=user).values(
            'event_type', 'is_system_enabled', 'is_email_enabled'
        )

        user_settings, _ = UserNotificationSettings.objects.get_or_create(user=user)

        return Response({
            'event_types': [
                {'key': e.key, 'title': e.title_tpl} for e in EVENTS.values()
            ],
            'configs': list(db_configs),
            'global_config': {
                'emails_disabled_globally': user_settings.emails_disabled_globally
            }
        })


class NotificationConfigUpdateView(APIView):
    """Updates personal config for the authenticated user only."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_type = request.data.get('event_type')
        is_system = request.data.get('is_system_enabled')
        is_email = request.data.get('is_email_enabled')

        config = get_object_or_404(NotificationConfig, user=request.user, event_type=event_type)
        if is_system is not None:
            config.is_system_enabled = is_system
        if is_email is not None:
            config.is_email_enabled = is_email
        config.save()

        return Response({'detail': f'Setting updated for {event_type}'})


class GlobalConfigUpdateView(APIView):
    """Updates personal global notification settings for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        disabled = request.data.get('emails_disabled_globally')

        user_settings, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
        if disabled is not None:
            user_settings.emails_disabled_globally = disabled
            user_settings.save()

        return Response({'detail': 'Personal global email setting updated'})
