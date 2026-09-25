from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from backend.auth import JWTAuth

from .config import EVENTS
from .models import Notification, NotificationConfig, UserNotificationSettings
from .realtime import emit_notifications_deleted, emit_read_status_changed, emit_unread_count_updated

from backend.schemas import ErrorResponse
from .schemas import DeletedCountResponse, DetailResponse, GlobalConfigUpdateRequest, MarkedCountResponse, NotificationConfigUpdateRequest, NotificationResponse, NotificationSettingsResponse, UnreadCountResponse

router = Router(tags=['notifications'], auth=JWTAuth())


def _emit_unread_count(user):
    emit_unread_count_updated(user.id, Notification.objects.filter(recipient=user, is_read=False).count())


@router.get('', operation_id='listNotifications', response={200: list[NotificationResponse], 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=10)
def list_notifications(request):
    Notification.objects.filter(recipient=request.auth, created_at__lt=timezone.now() - timedelta(days=30)).delete()
    queryset = Notification.objects.filter(recipient=request.auth)
    
    return [NotificationResponse.model_validate(notification, from_attributes=True) for notification in queryset]


@router.post('/{notification_id}/read', operation_id='markNotificationRead', response={200: DetailResponse, 401: ErrorResponse, 404: ErrorResponse})
def mark_notification_read(request, notification_id: int):
    notification = Notification.objects.filter(id=notification_id, recipient=request.auth, is_read=False).first()
    
    if notification is None:
        raise HttpError(404, 'Notification not found or already read.')
    
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    
    emit_read_status_changed(request.auth.id, [notification.id], True)
    _emit_unread_count(request.auth)
    
    return DetailResponse(
        detail='Marked as read.',
    )


@router.post('/read-all', operation_id='markAllNotificationsRead', response={200: MarkedCountResponse, 401: ErrorResponse})
def mark_all_notifications_read(request):
    unread = Notification.objects.filter(recipient=request.auth, is_read=False)
    ids = list(unread.values_list('id', flat=True))
    marked = unread.update(is_read=True)
    
    if ids:
        emit_read_status_changed(request.auth.id, ids, True)
    _emit_unread_count(request.auth)
    
    return MarkedCountResponse(
        marked=marked,
    )


@router.get('/unread-count', operation_id='getUnreadNotificationCount', response={200: UnreadCountResponse, 401: ErrorResponse})
def get_unread_count(request):
    unread_count = Notification.objects.filter(recipient=request.auth, is_read=False).count()
    
    return UnreadCountResponse(
        unread_count=unread_count,
    )


@router.delete('/delete-all', operation_id='deleteAllNotifications', response={200: DeletedCountResponse, 401: ErrorResponse})
def delete_all_notifications(request):
    notifications = Notification.objects.filter(recipient=request.auth)
    ids = list(notifications.values_list('id', flat=True))
    deleted, _ = notifications.delete()
    
    if ids:
        emit_notifications_deleted(request.auth.id, ids)
    _emit_unread_count(request.auth)
    
    return DeletedCountResponse(
        deleted=deleted,
    )


@router.get('/settings', operation_id='getNotificationSettings', response={200: NotificationSettingsResponse, 401: ErrorResponse})
def get_notification_settings(request):
    for event_type, event in EVENTS.items():
        NotificationConfig.objects.get_or_create(user=request.auth, event_type=event_type, defaults={'is_system_enabled': 'system' in event.channels, 'is_email_enabled': 'email' in event.channels})
    
    settings, _ = UserNotificationSettings.objects.get_or_create(user=request.auth)
    
    return NotificationSettingsResponse(
        event_types=[
            {
                'key': event.key,
                'title': event.title_tpl,
            }
            for event in EVENTS.values()
        ],
        configs=list(
            NotificationConfig.objects.filter(user=request.auth).values(
                'event_type',
                'is_system_enabled',
                'is_email_enabled',
            )
        ),
        global_config={
            'emails_disabled_globally': settings.emails_disabled_globally,
        },
    )


@router.put('/settings', operation_id='updateNotificationSettings', response={200: NotificationSettingsResponse, 401: ErrorResponse})
def update_notification_settings(request):
    return get_notification_settings(request)


@router.post('/settings/config/update', operation_id='updateNotificationConfig', response={200: DetailResponse, 401: ErrorResponse, 404: ErrorResponse})
def update_notification_config(request, payload: NotificationConfigUpdateRequest):
    config = get_object_or_404(NotificationConfig, user=request.auth, event_type=payload.event_type)
    
    if payload.is_system_enabled is not None:
        config.is_system_enabled = payload.is_system_enabled
    if payload.is_email_enabled is not None:
        config.is_email_enabled = payload.is_email_enabled
    
    config.save()
    return DetailResponse(
        detail=f'Setting updated for {payload.event_type}',
    )

@router.post('/settings/global/update', operation_id='updateGlobalNotificationConfig', response={200: DetailResponse, 401: ErrorResponse})
def update_global_notification_config(request, payload: GlobalConfigUpdateRequest):
    settings, _ = UserNotificationSettings.objects.get_or_create(user=request.auth)
    settings.emails_disabled_globally = payload.emails_disabled_globally
    
    settings.save(update_fields=['emails_disabled_globally'])
    return DetailResponse(
        detail='Personal global email setting updated',
    )


@router.delete('/{notification_id}', operation_id='deleteNotification', response={204: None, 401: ErrorResponse, 404: ErrorResponse})
def delete_notification(request, notification_id: int):
    notification = Notification.objects.filter(id=notification_id, recipient=request.auth).first()

    if notification is None:
        raise HttpError(404, 'Notification not found.')
    notification.delete()

    emit_notifications_deleted(request.auth.id, [notification_id])
    _emit_unread_count(request.auth)

    return 204, None
