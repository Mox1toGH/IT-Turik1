from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    Stores a system (in-site) notification for a user.

    Each row represents one notification delivered via the 'system' channel.
    Email notifications are sent inline and do NOT create a row here.
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
