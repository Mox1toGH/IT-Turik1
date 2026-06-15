import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .channels import CHANNEL_REGISTRY
from .models import NotificationDeliveryTask

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix='notifications-dispatch')
_SCHEDULE_LOCK = threading.Lock()
_WORKER_RUNNING = False
_MAX_ATTEMPTS = 6


def dispatch_pending_async() -> None:
    global _WORKER_RUNNING
    with _SCHEDULE_LOCK:
        if _WORKER_RUNNING:
            return
        _WORKER_RUNNING = True
    _EXECUTOR.submit(_drain_pending_tasks)


def _drain_pending_tasks(batch_size: int = 50) -> None:
    global _WORKER_RUNNING
    try:
        _requeue_stale_processing_tasks()
        while True:
            processed = _process_batch(batch_size=batch_size)
            if processed == 0:
                return
    finally:
        with _SCHEDULE_LOCK:
            _WORKER_RUNNING = False


def _process_batch(batch_size: int = 50) -> int:
    now = timezone.now()
    with transaction.atomic():
        task_ids = list(
            NotificationDeliveryTask.objects.select_for_update(skip_locked=True)
            .filter(
                status=NotificationDeliveryTask.STATUS_PENDING,
                next_attempt_at__lte=now,
            )
            .order_by('created_at')
            .values_list('id', flat=True)[:batch_size]
        )
        if not task_ids:
            return 0

        NotificationDeliveryTask.objects.filter(id__in=task_ids).update(
            status=NotificationDeliveryTask.STATUS_PROCESSING,
        )

    tasks = list(
        NotificationDeliveryTask.objects.select_related('recipient')
        .filter(id__in=task_ids)
        .order_by('created_at')
    )

    for task in tasks:
        channel_cls = CHANNEL_REGISTRY.get(task.channel)
        if not channel_cls:
            _mark_failed(task, 'Unknown channel configured.')
            continue

        try:
            channel = channel_cls()
            channel.send(
                recipient=task.recipient,
                title=task.title,
                message=task.message,
                event_type=task.event_type,
                email_subject=task.email_subject,
            )
            NotificationDeliveryTask.objects.filter(id=task.id).update(
                status=NotificationDeliveryTask.STATUS_SENT,
                attempts=task.attempts + 1,
                last_error='',
                updated_at=timezone.now(),
            )
        except Exception as exc:
            logger.exception(
                'Notification dispatch failed: task_id=%s channel=%s event=%s',
                task.id,
                task.channel,
                task.event_type,
            )
            _mark_failed(task, str(exc))

    return len(tasks)


def _requeue_stale_processing_tasks(stale_after_minutes: int = 5) -> None:
    stale_before = timezone.now() - timedelta(minutes=stale_after_minutes)
    NotificationDeliveryTask.objects.filter(
        status=NotificationDeliveryTask.STATUS_PROCESSING,
        updated_at__lt=stale_before,
    ).update(
        status=NotificationDeliveryTask.STATUS_PENDING,
        next_attempt_at=timezone.now(),
    )


def _mark_failed(task: NotificationDeliveryTask, error_message: str) -> None:
    next_attempt = task.attempts + 1
    if next_attempt >= _MAX_ATTEMPTS:
        NotificationDeliveryTask.objects.filter(id=task.id).update(
            status=NotificationDeliveryTask.STATUS_FAILED,
            attempts=next_attempt,
            last_error=error_message[:2000],
            updated_at=timezone.now(),
        )
        return

    retry_delay = timedelta(seconds=min(300, 2 ** next_attempt))
    NotificationDeliveryTask.objects.filter(id=task.id).update(
        status=NotificationDeliveryTask.STATUS_PENDING,
        attempts=next_attempt,
        last_error=error_message[:2000],
        next_attempt_at=timezone.now() + retry_delay,
        updated_at=timezone.now(),
    )
