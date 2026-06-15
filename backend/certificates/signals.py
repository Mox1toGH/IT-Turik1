from django.db.models.signals import post_save
from django.dispatch import receiver

from certificates.models import Certificate
from notifications.services import NotificationService


@receiver(post_save, sender=Certificate)
def handle_certificate_created(sender, instance: Certificate, created: bool, **kwargs):
    if not created or not instance.user_id:
        return

    NotificationService.notify(
        recipients=[instance.user],
        event_type='certificate_received',
        context={
            'tournament_name': instance.tournament_name or 'Tournament',
            'placement': instance.placement or 'Participant',
            'certificate_number': instance.certificate_number or str(instance.unique_code),
        },
    )
