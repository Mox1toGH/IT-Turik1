import base64
import hashlib
import logging
import os

from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URI = 'https://oauth2.googleapis.com/token'


def _generate_code_verifier():
    """Generate a PKCE code verifier (43-128 chars, URL-safe base64)."""
    return base64.urlsafe_b64encode(os.urandom(40)).rstrip(b'=').decode('ascii')


def _generate_code_challenge(verifier):
    """Generate a PKCE S256 code challenge from a verifier."""
    digest = hashlib.sha256(verifier.encode('ascii')).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')


def _get_calendar_service(user):
    token_data = user.google_calendar_token

    if not token_data:
        return None

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=GOOGLE_TOKEN_URI,
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request

        try:
            creds.refresh(Request())

            user.google_calendar_token = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
            }
            user.save(update_fields=['google_calendar_token'])

        except Exception:
            logger.exception(
                'Failed to refresh Google Calendar token for user %s',
                user.id,
            )

            user.google_calendar_token = None
            user.google_calendar_connected = False
            user.save(
                update_fields=[
                    'google_calendar_token',
                    'google_calendar_connected',
                ]
            )

            raise

    return build(
        'calendar',
        'v3',
        credentials=creds,
    )


def _sync_all_calendar_items(user):
    """Sync all existing events and rounds from user's tournaments to Google Calendar."""
    import datetime

    from backend.permissions import Permission, has_permission as user_has_permission
    from teams.models import Team, TeamMember
    from tournaments.models import (
        Event,
        Round,
        Tournament,
        TournamentTeamRegistration,
    )

    service = _get_calendar_service(user)

    if not service:
        raise RuntimeError('Google Calendar is not connected.')

    try:
        if user_has_permission(user, Permission.VIEW_TOURNAMENT):
            tournament_ids = Tournament.objects.exclude(
                status=Tournament.STATUS_DRAFT
            ).values_list('id', flat=True)

        else:
            captain_teams = Team.objects.filter(
                captain=user
            ).values_list('id', flat=True)

            member_teams = TeamMember.objects.filter(
                user=user
            ).values_list('team_id', flat=True)

            team_ids = set(captain_teams) | set(member_teams)

            tournament_ids = TournamentTeamRegistration.objects.filter(
                team_id__in=team_ids,
                is_active=True,
            ).values_list('tournament_id', flat=True)

    except Exception:
        logger.exception(
            'Failed to get tournaments for calendar sync. User: %s',
            user.id,
        )
        raise

    events = Event.objects.filter(
        tournament_id__in=tournament_ids
    ).select_related('tournament')

    for event in events:
        try:
            start_dt = event.start_datetime
            end_dt = start_dt + datetime.timedelta(hours=1)

            body = {
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
                body['description'] += f'\n\nLink: {event.link}'

            service.events().insert(
                calendarId='primary',
                body=body,
            ).execute()

        except Exception:
            logger.exception(
                'Failed to sync event %s for user %s',
                event.id,
                user.id,
            )
            raise

    rounds = Round.objects.filter(
        tournament_id__in=tournament_ids
    ).select_related('tournament')

    for round_obj in rounds:
        try:
            start_event = {
                'summary': f'{round_obj.name} starts — {round_obj.tournament.name}',
                'description': f'Round starts for tournament {round_obj.tournament.name}',
                'start': {
                    'dateTime': round_obj.start_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (
                        round_obj.start_date + datetime.timedelta(hours=1)
                    ).isoformat(),
                    'timeZone': 'UTC',
                },
            }

            service.events().insert(
                calendarId='primary',
                body=start_event,
            ).execute()

            deadline_event = {
                'summary': f'{round_obj.name} deadline — {round_obj.tournament.name}',
                'description': f'Submission deadline for {round_obj.name}',
                'start': {
                    'dateTime': round_obj.end_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (
                        round_obj.end_date + datetime.timedelta(minutes=30)
                    ).isoformat(),
                    'timeZone': 'UTC',
                },
            }

            service.events().insert(
                calendarId='primary',
                body=deadline_event,
            ).execute()

        except Exception:
            logger.exception(
                'Failed to sync round %s for user %s',
                round_obj.id,
                user.id,
            )
            raise

    logger.info(
        'Auto-synced all calendar items for user %s',
        user.id,
    )