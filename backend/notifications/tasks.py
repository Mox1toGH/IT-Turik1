import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="notifications.drain_pending_deliveries")
def drain_pending_deliveries() -> None:
    """Process queued NotificationDeliveryTask rows.

    Runs periodically via Celery beat, so retries whose ``next_attempt_at``
    has passed get delivered even if no new notification triggers the
    in-process dispatcher.
    """
    from .dispatcher import drain_pending_tasks

    drain_pending_tasks()
