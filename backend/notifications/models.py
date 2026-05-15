from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """
    Stores a system (in-site) notification for a user.

    Each row represents one notification delivered via the 'system' channel.
    Email notifications are delivered via delivery tasks and do NOT create a row here.
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    event_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read'], name='notif_recipient_read_idx'),
            models.Index(fields=['recipient', 'created_at'], name='notif_recipient_date_idx'),
        ]

    def __str__(self):
        return f'{self.event_type} → {self.recipient_id} (read={self.is_read})'


class UserNotificationSettings(models.Model):
    """Global notification toggles for a specific user."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    emails_disabled_globally = models.BooleanField(
        default=False,
        help_text="If True, this user will never receive any notification emails."
    )

    class Meta:
        verbose_name = "User Notification Setting"
        verbose_name_plural = "User Notification Settings"

    def __str__(self):
        return f"Settings for {self.user.username}"


class NotificationConfig(models.Model):
    """Per-user configuration for a specific event type."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_configs'
    )
    event_type = models.CharField(max_length=64)
    is_system_enabled = models.BooleanField(default=True)
    is_email_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'event_type')
        verbose_name = "User Event Config"
        verbose_name_plural = "User Event Configs"

    def __str__(self):
        return f"{self.user.username} - {self.event_type}"


class NotificationDeliveryTask(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_delivery_tasks',
    )
    channel = models.CharField(max_length=32)
    event_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    email_subject = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)
    next_attempt_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status', 'next_attempt_at'], name='notif_task_status_next_idx'),
            models.Index(fields=['recipient', 'created_at'], name='notif_task_recipient_date_idx'),
        ]

    def __str__(self):
        return f'{self.channel}:{self.event_type} -> {self.recipient_id} ({self.status})'
