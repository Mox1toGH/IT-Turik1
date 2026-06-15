from django.core.management.base import BaseCommand

from notifications.dispatcher import _drain_pending_tasks


class Command(BaseCommand):
    help = 'Process pending notification delivery tasks from the DB queue.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='How many queued tasks to process per DB lock batch.',
        )

    def handle(self, *args, **options):
        batch_size = max(1, int(options['batch_size']))
        _drain_pending_tasks(batch_size=batch_size)
        self.stdout.write(self.style.SUCCESS('Notification queue processed.'))
