import base64
import hashlib
import logging
import os

import requests as http_requests
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
            logger.exception('Failed to refresh Google Calendar token')
            user.google_calendar_token = None
            user.google_calendar_connected = False
            user.save(update_fields=['google_calendar_token', 'google_calendar_connected'])
            return None

    return build('calendar', 'v3', credentials=creds)


def _sync_all_calendar_items(user):
    """Sync all existing events and rounds from the user's tournaments to Google Calendar."""
    import datetime
    from django.db.models import Q

    service = _get_calendar_service(user)
    if not service:
        return

    from tournaments.models import (
        Event, Round, Tournament, TournamentTeamRegistration,
    )
    from backend.permissions import Permission, has_permission as user_has_permission
    from teams.models import Team, TeamMember

    # Find tournament IDs this user participates in
    try:
        if user_has_permission(user, Permission.VIEW_TOURNAMENT):
            tournament_ids = Tournament.objects.exclude(
                status=Tournament.STATUS_DRAFT
            ).values_list('id', flat=True)
        else:
            team_ids = set()
            captain_teams = Team.objects.filter(captain=user).values_list('id', flat=True)
            member_teams = TeamMember.objects.filter(user=user).values_list('team_id', flat=True)
            team_ids = set(captain_teams) | set(member_teams)

            tournament_ids = TournamentTeamRegistration.objects.filter(
                team_id__in=team_ids,
                is_active=True,
            ).values_list('tournament_id', flat=True)
    except Exception:
        logger.exception('Failed to get tournament IDs for user %s', user.id)
        return

    # Sync events
    events = Event.objects.filter(
        tournament_id__in=tournament_ids
    ).select_related('tournament')

    for event in events:
        try:
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
        except Exception:
            logger.exception('Failed to sync event %s for user %s', event.id, user.id)

    # Sync rounds
    rounds = Round.objects.filter(
        tournament_id__in=tournament_ids
    ).select_related('tournament')

    for round_obj in rounds:
        try:
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
        except Exception:
            logger.exception('Failed to sync round %s for user %s', round_obj.id, user.id)

    logger.info('Auto-synced all calendar items for user %s', user.id)


class GoogleCalendarStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'connected': request.user.google_calendar_connected,
        })


class GoogleCalendarConnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.GOOGLE_OAUTH_CLIENT_SECRET:
            return Response(
                {'detail': 'Google Calendar integration is not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Generate PKCE pair
        code_verifier = _generate_code_verifier()
        code_challenge = _generate_code_challenge(code_verifier)

        # Build the authorization URL manually (no library PKCE interference)
        from urllib.parse import urlencode
        params = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_CALENDAR_REDIRECT_URI,
            'response_type': 'code',
            'scope': ' '.join(SCOPES),
            'access_type': 'offline',
            'prompt': 'consent',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        }
        auth_url = f'{GOOGLE_AUTH_URI}?{urlencode(params)}'

        # Store the code_verifier for callback
        request.user.google_calendar_token = {
            '_code_verifier': code_verifier,
        }
        request.user.save(update_fields=['google_calendar_token'])

        return Response({'auth_url': auth_url})


class GoogleCalendarCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response(
                {'detail': 'Authorization code is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Restore the PKCE code_verifier
            token_data = request.user.google_calendar_token or {}
            code_verifier = token_data.get('_code_verifier')

            # Exchange code for tokens using plain HTTP (no library PKCE conflicts)
            token_response = http_requests.post(GOOGLE_TOKEN_URI, data={
                'code': code,
                'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_CALENDAR_REDIRECT_URI,
                'grant_type': 'authorization_code',
                'code_verifier': code_verifier,
            })

            if token_response.status_code != 200:
                error_data = token_response.json()
                error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                logger.error('Google token exchange failed: %s', error_data)
                return Response(
                    {'detail': f'Token exchange failed: {error_msg}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tokens = token_response.json()

            user = request.user
            user.google_calendar_token = {
                'token': tokens.get('access_token'),
                'refresh_token': tokens.get('refresh_token'),
            }
            user.google_calendar_connected = True
            user.save(update_fields=['google_calendar_token', 'google_calendar_connected'])

            # Auto-sync all existing events/rounds to Google Calendar
            _sync_all_calendar_items(user)

            return Response({'connected': True})

        except Exception as e:
            logger.exception('Google Calendar OAuth callback failed')
            return Response(
                {'detail': f'Failed to connect: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GoogleCalendarDisconnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.google_calendar_token = None
        user.google_calendar_connected = False
        user.save(update_fields=['google_calendar_token', 'google_calendar_connected'])
        return Response({'connected': False})
