import datetime
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.google_calendar import _get_calendar_service
from .models import Event, Round, TournamentTeamRegistration

logger = logging.getLogger(__name__)


def _get_connected_users_for_tournament(tournament_id):
    """Return User queryset of ALL users who should see this tournament's events
    and have Google Calendar connected.

    Includes:
    - Members/captains of teams registered in the tournament
    - Admin users (they see all tournaments)
    """
    from accounts.models import User
    from teams.models import Team, TeamMember

    registrations = TournamentTeamRegistration.objects.filter(
        tournament_id=tournament_id,
        is_active=True,
    )

    team_ids = registrations.values_list('team_id', flat=True)

    captain_ids = Team.objects.filter(id__in=team_ids).values_list('captain_id', flat=True)
    member_ids = TeamMember.objects.filter(team_id__in=team_ids).values_list('user_id', flat=True)

    user_ids = set(captain_ids) | set(member_ids)

    # Also include admin users — they see all tournaments
    admin_ids = User.objects.filter(
        role='admin',
        google_calendar_connected=True,
    ).exclude(google_calendar_token__isnull=True).values_list('id', flat=True)

    user_ids |= set(admin_ids)

    return User.objects.filter(
        id__in=user_ids,
        google_calendar_connected=True,
    ).exclude(google_calendar_token__isnull=True)


@receiver(post_save, sender=Event)
def sync_event_to_google_calendar(sender, instance, created, **kwargs):
    """When an Event is created, push it to all connected users' Google Calendars."""
    if not created:
        return

    event = instance
    logger.info('Signal fired: new Event %s created for tournament %s', event.id, event.tournament_id)

    users = _get_connected_users_for_tournament(event.tournament_id)

    for user in users:
        try:
            service = _get_calendar_service(user)
            if not service:
                logger.warning('Could not get calendar service for user %s', user.id)
                continue

            start_dt = event.start_datetime
            end_dt = start_dt + datetime.timedelta(hours=1)

            gcal_event = {
                'summary': f'{event.title} — {event.tournament.name}',
                'description': event.description or '',
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            if event.link:
                gcal_event['description'] += f'\n\nLink: {event.link}'

            service.events().insert(calendarId='primary', body=gcal_event).execute()
            logger.info('Auto-synced event %s to Google Calendar for user %s', event.id, user.id)
        except Exception:
            logger.exception('Failed to auto-sync event %s for user %s', event.id, user.id)


@receiver(post_save, sender=Round)
def sync_round_to_google_calendar(sender, instance, created, **kwargs):
    """When a Round is created, push start + deadline to all connected users' Google Calendars."""
    if not created:
        return

    round_obj = instance
    logger.info('Signal fired: new Round %s created for tournament %s', round_obj.id, round_obj.tournament_id)
    print(f'[GCal Signal] New Round {round_obj.id} created for tournament {round_obj.tournament_id}')

    users = _get_connected_users_for_tournament(round_obj.tournament_id)
    print(f'[GCal Signal] Found {users.count()} connected users to sync round {round_obj.id}')

    for user in users:
        try:
            service = _get_calendar_service(user)
            if not service:
                logger.warning('Could not get calendar service for user %s', user.id)
                continue

            # Round start event
            gcal_start = {
                'summary': f'{round_obj.name} starts — {round_obj.tournament.name}',
                'description': f'Round starts for tournament {round_obj.tournament.name}',
                'start': {
                    'dateTime': round_obj.start_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (round_obj.start_date + datetime.timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                },
            }
            service.events().insert(calendarId='primary', body=gcal_start).execute()

            # Round deadline event
            gcal_deadline = {
                'summary': f'{round_obj.name} deadline — {round_obj.tournament.name}',
                'description': f'Submission deadline for {round_obj.name}',
                'start': {
                    'dateTime': round_obj.end_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (round_obj.end_date + datetime.timedelta(minutes=30)).isoformat(),
                    'timeZone': 'UTC',
                },
            }
            service.events().insert(calendarId='primary', body=gcal_deadline).execute()

            logger.info('Auto-synced round %s to Google Calendar for user %s', round_obj.id, user.id)
        except Exception:
            logger.exception('Failed to auto-sync round %s for user %s', round_obj.id, user.id)
