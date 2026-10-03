import logging
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.pagination import PageNumberPagination, paginate

from backend.auth import JWTAuth

from .config import EVENTS
from .models import Notification, NotificationConfig, UserNotificationSettings
from .realtime import emit_notifications_deleted, emit_read_status_changed, emit_unread_count_updated

from backend.schemas import ErrorResponse
from backend.errors import raise_api_error
from http import HTTPStatus
from .schemas import DeletedCountResponse, DetailResponse, GlobalConfigUpdateRequest, MarkedCountResponse, NotificationConfigUpdateRequest, NotificationResponse, NotificationSettingsResponse, UnreadCountResponse

logger = logging.getLogger(__name__)

router = Router(tags=['notifications'], auth=JWTAuth())


def _emit_unread_count(user):
    unread_count = Notification.objects.filter(recipient=user, is_read=False).count()
    emit_unread_count_updated(user.id, unread_count)
    logger.debug(
        'Unread count emitted',
        extra={'user_id': user.id, 'unread_count': unread_count},
    )


@router.get('', operation_id='listNotifications', url_name="notification-list", response={200: list[NotificationResponse], 401: ErrorResponse})
@paginate(PageNumberPagination, page_size=10)
def list_notifications(request):
    logger.debug('Listing notifications', extra={'user_id': request.auth.id})
    expired_count, _ = Notification.objects.filter(recipient=request.auth, created_at__lt=timezone.now() - timedelta(days=30)).delete()
    if expired_count:
        logger.info(
            'Expired notifications purged',
            extra={'user_id': request.auth.id, 'deleted_count': expired_count},
        )
    queryset = Notification.objects.filter(recipient=request.auth)
    
    return [NotificationResponse.model_validate(notification, from_attributes=True) for notification in queryset]


@router.post('/{notification_id}/read', operation_id='markNotificationRead', url_name="notification-mark-read", response={200: DetailResponse, 401: ErrorResponse, 404: ErrorResponse})
def mark_notification_read(request, notification_id: int):
    notification = Notification.objects.filter(id=notification_id, recipient=request.auth, is_read=False).first()
    
    if notification is None:
        logger.warning(
            'Mark read rejected, not found or already read',
            extra={'notification_id': notification_id, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.NOT_FOUND, 'Notification not found or already read.')
    
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    logger.info(
        'Notification marked read',
        extra={'notification_id': notification.id, 'user_id': request.auth.id},
    )
    
    emit_read_status_changed(request.auth.id, [notification.id], True)
    _emit_unread_count(request.auth)
    
    return DetailResponse(
        detail='Marked as read.',
    )


@router.post('/read-all', operation_id='markAllNotificationsRead', url_name="notification-mark-all-read", response={200: MarkedCountResponse, 401: ErrorResponse})
def mark_all_notifications_read(request):
    unread = Notification.objects.filter(recipient=request.auth, is_read=False)
    ids = list(unread.values_list('id', flat=True))
    marked = unread.update(is_read=True)
    logger.info(
        'All notifications marked read',
        extra={'user_id': request.auth.id, 'marked_count': marked},
    )
    
    if ids:
        emit_read_status_changed(request.auth.id, ids, True)
    _emit_unread_count(request.auth)
    
    return MarkedCountResponse(
        marked=marked,
    )


@router.get('/unread-count', operation_id='getUnreadNotificationCount', url_name="notification-unread-count", response={200: UnreadCountResponse, 401: ErrorResponse})
def get_unread_count(request):
    unread_count = Notification.objects.filter(recipient=request.auth, is_read=False).count()
    logger.debug(
        'Fetched unread count',
        extra={'user_id': request.auth.id, 'unread_count': unread_count},
    )
    
    return UnreadCountResponse(
        unread_count=unread_count,
    )


@router.delete('/delete-all', operation_id='deleteAllNotifications', url_name="notification-delete-all", response={200: DeletedCountResponse, 401: ErrorResponse})
def delete_all_notifications(request):
    notifications = Notification.objects.filter(recipient=request.auth)
    ids = list(notifications.values_list('id', flat=True))
    deleted, _ = notifications.delete()
    logger.info(
        'All notifications deleted',
        extra={'user_id': request.auth.id, 'deleted_count': deleted},
    )
    
    if ids:
        emit_notifications_deleted(request.auth.id, ids)
    _emit_unread_count(request.auth)
    
    return DeletedCountResponse(
        deleted=deleted,
    )


@router.get('/settings', operation_id='getNotificationSettings', url_name="notification-settings", response={200: NotificationSettingsResponse, 401: ErrorResponse})
def get_notification_settings(request):
    logger.debug('Fetching notification settings', extra={'user_id': request.auth.id})
    created_count = 0
    for event_type, event in EVENTS.items():
        _, created = NotificationConfig.objects.get_or_create(user=request.auth, event_type=event_type, defaults={'is_system_enabled': 'system' in event.channels, 'is_email_enabled': 'email' in event.channels})
        if created:
            created_count += 1
    if created_count:
        logger.info(
            'Notification configs initialised',
            extra={'user_id': request.auth.id, 'created_count': created_count},
        )
    
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


@router.put('/settings', operation_id='updateNotificationSettings', url_name="notification-settings", response={200: NotificationSettingsResponse, 401: ErrorResponse})
def update_notification_settings(request):
    return get_notification_settings(request)


@router.post('/settings/config/update', operation_id='updateNotificationConfig', url_name="notification-settings-config-update", response={200: DetailResponse, 401: ErrorResponse, 404: ErrorResponse})
def update_notification_config(request, payload: NotificationConfigUpdateRequest):
    config = get_object_or_404(NotificationConfig, user=request.auth, event_type=payload.event_type)
    
    if payload.is_system_enabled is not None:
        config.is_system_enabled = payload.is_system_enabled
    if payload.is_email_enabled is not None:
        config.is_email_enabled = payload.is_email_enabled
    
    config.save()
    logger.info(
        'Notification config updated',
        extra={
            'user_id': request.auth.id,
            'event_type': payload.event_type,
            'is_system_enabled': config.is_system_enabled,
            'is_email_enabled': config.is_email_enabled,
        },
    )
    return DetailResponse(
        detail=f'Setting updated for {payload.event_type}',
    )

@router.post('/settings/global/update', operation_id='updateGlobalNotificationConfig', url_name="notification-settings-global-update", response={200: DetailResponse, 401: ErrorResponse})
def update_global_notification_config(request, payload: GlobalConfigUpdateRequest):
    settings, _ = UserNotificationSettings.objects.get_or_create(user=request.auth)
    settings.emails_disabled_globally = payload.emails_disabled_globally
    
    settings.save(update_fields=['emails_disabled_globally'])
    logger.info(
        'Global notification setting updated',
        extra={
            'user_id': request.auth.id,
            'emails_disabled_globally': settings.emails_disabled_globally,
        },
    )
    return DetailResponse(
        detail='Personal global email setting updated',
    )


@router.delete('/{notification_id}', operation_id='deleteNotification', url_name='notification-delete', response={204: None, 401: ErrorResponse, 404: ErrorResponse})
def delete_notification(request, notification_id: int):
    notification = Notification.objects.filter(id=notification_id, recipient=request.auth).first()

    if notification is None:
        logger.warning(
            'Notification delete rejected, not found',
            extra={'notification_id': notification_id, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.NOT_FOUND, 'Notification not found.')
    notification.delete()
    logger.info(
        'Notification deleted',
        extra={'notification_id': notification_id, 'user_id': request.auth.id},
    )

    emit_notifications_deleted(request.auth.id, [notification_id])
    _emit_unread_count(request.auth)

    return 204, None