import asyncio

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count

from .models import Notification
from .schemas import NotificationResponse


def _group_name(user_id: int) -> str:
    return f'notifications.user.{user_id}'


def _send(user_id: int, event_name: str, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        _group_name(user_id),
        {
            'type': 'notification_event',
            'event': event_name,
            'payload': payload,
        },
    )


def emit_notification_created(notification) -> None:
    _send(
        notification.recipient_id,
        'notification.created',
        {'notification': NotificationResponse.model_validate(
            notification, from_attributes=True
        ).model_dump(mode='json'),},
    )


def emit_notifications_created(notifications) -> None:
    if not notifications:
        return

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    recipient_ids = {notification.recipient_id for notification in notifications}
    unread_counts = dict(
        Notification.objects.filter(
            recipient_id__in=recipient_ids,
            is_read=False,
        )
        .values('recipient_id')
        .annotate(unread_count=Count('id'))
        .values_list('recipient_id', 'unread_count')
    )
    events = []
    for notification in notifications:
        events.extend(
            (
                (
                    notification.recipient_id,
                    'notification.created',
                    {
                        'notification': NotificationResponse.model_validate(
                            notification,
                            from_attributes=True,
                        ).model_dump(mode='json'),
                    },
                ),
                (
                    notification.recipient_id,
                    'notification.unread_count_updated',
                    {
                        'unread_count': unread_counts.get(
                            notification.recipient_id,
                            0,
                        ),
                    },
                ),
            )
        )

    async def send_events():
        await asyncio.gather(
            *(
                channel_layer.group_send(
                    _group_name(user_id),
                    {
                        'type': 'notification_event',
                        'event': event_name,
                        'payload': payload,
                    },
                )
                for user_id, event_name, payload in events
            )
        )

    async_to_sync(send_events)()


def emit_unread_count_updated(user_id: int, unread_count: int) -> None:
    _send(user_id, 'notification.unread_count_updated', {'unread_count': unread_count})


def emit_read_status_changed(user_id: int, notification_ids: list[int], is_read: bool) -> None:
    _send(
        user_id,
        'notification.read_status_changed',
        {
            'notification_ids': notification_ids,
            'is_read': is_read,
        },
    )


def emit_notifications_deleted(user_id: int, notification_ids: list[int]) -> None:
    _send(
        user_id,
        'notification.deleted',
        {
            'notification_ids': notification_ids,
        },
    )
