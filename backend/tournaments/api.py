import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from ninja import File, Router
from ninja.files import UploadedFile
from ninja.pagination import paginate
from backend.pagination import APIPageNumberPagination

from accounts.models import User
from accounts.google_calendar import get_calendar_service
from backend.auth import JWTAuth
from backend.media import absolute_media_url
from backend.permissions import Permission, require_permission, has_permission
from backend.uploads import validate_and_clean_image
from backend.schemas import ErrorResponse
from evaluation.leaderboard_service import get_tournament_leaderboard
from evaluation.models import LeaderboardEntry
from notifications.services import NotificationService
from teams.models import Team, TeamMember

from .models import Event, Round, Submission, Tournament, TournamentTeamRegistration
from backend.errors import raise_api_error
from http import HTTPStatus
from .schemas import (
    ActiveTournamentResponse, CurrentTaskResponse, EligibleTeamResponse,
    DisqualificationRequest, DisqualificationResponse, ExportToGoogleCalendarRequest,
    ExportToGoogleCalendarResponse, MyCalendarResponse,
    EventCreateRequest, EventResponse, EventUpdateRequest, OwnSubmissionResponse,
    RoundCreateRequest, RoundResponse, RoundUpdateRequest,
    SubmissionCreateRequest,
    SubmissionResponse, SubmissionUpdateRequest, TeamRegistrationRequest,
    TeamRegistrationResponse, TournamentArchiveDetailResponse,
    TournamentArchiveListResponse, TournamentCreateRequest, TournamentListResponse,
    TournamentResponse, TournamentTeamResponse, TournamentUpdateRequest,
    
)
from .services import (
    close_submissions_on_round, delete_round, leave_team_from_tournament,
    mark_round_evaluated, register_team_for_tournament, start_registration, start_round,
    sync_time_based_statuses,
)

logger = logging.getLogger(__name__)

router = Router(tags=['tournaments'], auth=JWTAuth())


def _tournaments():
    return Tournament.objects.prefetch_related(
        Prefetch('rounds', queryset=Round.objects.order_by('start_date'))
    ).order_by('-created_at')


def _rounds():
    return Round.objects.select_related('tournament').order_by('tournament_id', 'start_date')


def _submissions():
    return Submission.objects.select_related('team', 'round', 'round__tournament').prefetch_related(
        'jury_assignments__jury', 'jury_assignments__evaluation'
    )


def _criteria_data(criteria):
    return [
        criterion.model_dump() if hasattr(criterion, 'model_dump') else criterion
        for criterion in criteria
    ]


def _validation_error(error):
    if hasattr(error, 'message_dict'):
        message_dict = error.message_dict
        message = next(iter(message_dict.values()), ['Invalid input data.'])[0]
    else:
        message = error.messages[0] if getattr(error, 'messages', None) else 'Invalid input data.'
    logger.warning('Validation error', extra={'error_message': str(message)})
    raise_api_error(HTTPStatus.BAD_REQUEST, str(message))


def _validate_model(instance):
    try:
        instance.full_clean()
    except ValidationError as error:
        _validation_error(error)
    return instance


def _visible_tournaments(request):
    user = getattr(request, 'auth', None)
    queryset = _tournaments()
    if has_permission(user, Permission.VIEW_TOURNAMENT):
        return queryset
    published = ~Q(status=Tournament.STATUS_DRAFT)
    return queryset.filter(published | Q(created_by=user)) if user else queryset.filter(published)


def _participants(tournament: Tournament) -> list[User]:
    return list(
        User.objects.filter(
            Q(
                captained_teams__tournament_registrations__tournament=tournament,
                captained_teams__tournament_registrations__is_active=True,
            )
            | Q(
                teams__tournament_registrations__tournament=tournament,
                teams__tournament_registrations__is_active=True,
            )
        ).distinct()
    )


def _update_model(instance, values):
    for field, value in values.items():
        setattr(instance, field, value)
    return _validate_model(instance)


def _registered_team_ids(user):
    """Team IDs the user belongs to, as captain or member.

    This does not depend on the tournament, so callers must compute it once per
    request instead of per tournament; doing it inside the serialisation loop
    produced two identical queries for every row on the page.
    """
    if not (user and getattr(user, "is_authenticated", False)):
        return set()
    return set(user.teams.values_list("id", flat=True)) | set(
        Team.objects.filter(captain=user).values_list("id", flat=True)
    )


def _get_registered_team(tournament, request, team_ids=None):
    if 'rounds' not in getattr(tournament, '_prefetched_objects_cache', {}):
        tournament._prefetched_objects_cache = getattr(
            tournament, '_prefetched_objects_cache', {}
        )
        tournament._prefetched_objects_cache['rounds'] = list(
            Round.objects.filter(tournament_id=tournament.id).order_by('start_date')
        )

    user = getattr(request, "auth", None)

    if not (user and getattr(user, "is_authenticated", False)):
        return None

    if team_ids is None:
        team_ids = _registered_team_ids(user)

    registration = (
        tournament.team_registrations
        .filter(team_id__in=team_ids, is_active=True)
        .select_related("team")
        .first()
    )

    return registration.team if registration else None


def _tournament_response_data(tournament, request, team_ids=None):
    registered_team = _get_registered_team(tournament, request, team_ids)
    rounds = tournament._prefetched_objects_cache.get('rounds', [])
    return {
        'id': tournament.id,
        'name': tournament.name,
        'description': tournament.description,
        'start_date': tournament.start_date,
        'end_date': tournament.end_date,
        'max_teams': tournament.max_teams,
        'min_team_members': tournament.min_team_members,
        'banner': absolute_media_url(tournament.banner, {'request': request}),
        'status': tournament.status,
        'rounds': [
            {
                'id': round_obj.id,
                'name': round_obj.name,
                'start_date': round_obj.start_date,
                'end_date': round_obj.end_date,
                'status': round_obj.status,
                'criteria': _criteria_data(round_obj.criteria),
                'tournament': round_obj.tournament_id,
            }
            for round_obj in rounds
        ],
        'registered_team': (
            {'id': registered_team.id, 'name': registered_team.name, 'is_public': registered_team.is_public}
            if registered_team else None
        ),
    }


def _registration_response_data(registration):
    return {
        'id': registration.id,
        'tournament': registration.tournament_id,
        'team': registration.team_id,
        'team_name': registration.team.name,
        'is_active': registration.is_active,
        'is_disqualified': registration.is_disqualified,
        'disqualification_reason': registration.disqualification_reason,
        'created_at': registration.created_at,
    }


def _event_response_data(event):
    return {
        'id': event.id,
        'tournament': event.tournament_id,
        'type': event.type,
        'title': event.title,
        'description': event.description,
        'link': event.link,
        'start_datetime': event.start_datetime,
        'icon': event.icon_id,
        'created_at': event.created_at,
        'updated_at': event.updated_at,
    }


def _round_response_data(round_obj):
    return {
        'id': round_obj.id,
        'tournament': round_obj.tournament_id,
        'name': round_obj.name,
        'description': round_obj.description,
        'tech_requirements': round_obj.tech_requirements,
        'must_have_requirements': round_obj.must_have_requirements,
        'criteria': _criteria_data(round_obj.criteria),
        'start_date': round_obj.start_date,
        'end_date': round_obj.end_date,
        'passing_count': round_obj.passing_count,
        'evaluation_criteria': round_obj.evaluation_criteria,
        'materials': round_obj.materials,
        'status': round_obj.status,
    }


def _round_short_response_data(round_obj):
    return {
        'id': round_obj.id,
        'name': round_obj.name,
        'start_date': round_obj.start_date,
        'end_date': round_obj.end_date,
        'status': round_obj.status,
        'criteria': _criteria_data(round_obj.criteria),
        'tournament': round_obj.tournament_id,
    }


def _team_summary_response_data(team):
    return {'id': team.id, 'name': team.name, 'is_public': team.is_public}


def _submission_response_data(submission, request):
    assignments = submission._prefetched_objects_cache.get('jury_assignments', [])
    return {
        'id': submission.id,
        'team': submission.team_id,
        'round': submission.round_id,
        'team_details': _team_summary_response_data(submission.team),
        'round_details': _round_short_response_data(submission.round),
        'github_url': submission.github_url,
        'demo_video_url': submission.demo_video_url,
        'demo_video_file': absolute_media_url(submission.demo_video_file, {'request': request}),
        'live_demo_url': submission.live_demo_url,
        'description': submission.description,
        'assignments': [
            {
                'id': assignment.id,
                'jury': {
                    'id': assignment.jury_id,
                    'username': assignment.jury.username,
                    'full_name': assignment.jury.full_name,
                    'role': assignment.jury.role,
                },
                'evaluation': (
                    {
                        'id': assignment.evaluation.id,
                        'scores': assignment.evaluation.scores,
                        'total_score': assignment.evaluation.total_score,
                        'final_score': assignment.evaluation.final_score,
                        'comment': assignment.evaluation.comment,
                        'created_at': assignment.evaluation.created_at,
                    }
                    if getattr(assignment, 'evaluation', None) else None
                ),
                'created_at': assignment.created_at,
            }
            for assignment in assignments
        ],
        'created_at': submission.created_at,
        'updated_at': submission.updated_at,
    }


def _own_submission_response_data(submission, request):
    return {
        'id': submission.id,
        'team': _team_summary_response_data(submission.team),
        'round': _round_short_response_data(submission.round),
        'github_url': submission.github_url,
        'demo_video_url': submission.demo_video_url,
        'demo_video_file': absolute_media_url(submission.demo_video_file, {'request': request}),
        'live_demo_url': submission.live_demo_url,
        'description': submission.description,
        'created_at': submission.created_at,
        'updated_at': submission.updated_at,
    }


def _archive_standing_response_data(entry):
    return {
        'rank': entry.rank,
        'team': _team_summary_response_data(entry.team),
        'total_score': entry.total_score,
        'average_score': entry.average_score,
        'criteria_breakdown': entry.criteria_breakdown,
        'jury_breakdown': entry.jury_breakdown,
        'rounds_breakdown': entry.rounds_breakdown,
        'snapshot_at': entry.snapshot_at,
    }


def _archive_base_response_data(tournament, request):
    entries = tournament._prefetched_objects_cache.get('leaderboard_entries', [])
    return {
        'id': tournament.id,
        'name': tournament.name,
        'description': tournament.description,
        'start_date': tournament.start_date,
        'end_date': tournament.end_date,
        'status': tournament.status,
        'banner': absolute_media_url(tournament.banner, {'request': request}),
        'standings': [_archive_standing_response_data(entry) for entry in entries],
    }


def _tournament_team_response_data(registration, request):
    team = registration.team
    members = list(team._prefetched_objects_cache.get('members', []))
    if team.captain_id not in {member.id for member in members}:
        members.append(team.captain)
    return {
        'id': team.id,
        'registration_id': registration.id,
        'name': team.name,
        'members_count': len(members),
        'members': [
            {
                'id': member.id,
                'username': member.username,
                'email': member.email,
                'full_name': member.full_name,
                'role': member.role,
                'avatar': absolute_media_url(member.avatar, {'request': request}),
            }
            for member in members
        ],
        'is_public': team.is_public,
        'is_active': registration.is_active,
        'is_disqualified': registration.is_disqualified,
        'disqualification_reason': registration.disqualification_reason,
    }


def _team_participants(team: Team) -> list[User]:
    participants = {team.captain_id: team.captain} if team.captain_id else {}
    participants.update({member.id: member for member in team.members.all()})
    return list(participants.values())


@router.patch('/manage/{id}/banner', operation_id='updateTournamentBanner', url_name='tournament_manage_banner', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_tournament_banner(request, id: int, banner: UploadedFile = File(...)):
    require_permission(request, Permission.EDIT_TOURNAMENT)
    cleaned_banner, error = validate_and_clean_image(banner, max_size_bytes=5 * 1024 * 1024)
    if error:
        raise_api_error(HTTPStatus.BAD_REQUEST, error)
    tournament = get_object_or_404(Tournament, pk=id)

    try:
        tournament.banner = cleaned_banner
        tournament.save(update_fields=['banner'])
    finally:
        cleaned_banner.close()
    logger.info(
        'Tournament banner updated',
        extra={
            'tournament_id': id,
            'user_id': request.auth.id,
            'file_name': banner.name,
            'file_size': banner.size,
        },
    )

    return _tournament_response_data(tournament, request)


@router.delete('/manage/{id}/banner', operation_id='deleteTournamentBanner', url_name='tournament_manage_banner', response={200: TournamentResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_tournament_banner(request, id: int):
    require_permission(request, Permission.EDIT_TOURNAMENT)
    tournament = get_object_or_404(Tournament, pk=id)

    if tournament.banner:
        tournament.banner.delete(save=False)
        tournament.banner = None
        tournament.save(update_fields=['banner'])
        logger.info(
            'Tournament banner deleted',
            extra={'tournament_id': id, 'user_id': request.auth.id},
        )
    else:
        logger.debug('Banner delete requested but none set', extra={'tournament_id': id})

    return _tournament_response_data(tournament, request)


@router.get('/{id}/registrations/{registration_pk}', operation_id='getTournamentTeamRegistration', url_name='tournament_registration_detail', response={200: TeamRegistrationResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_tournament_team_registration(request, id: int, registration_pk: int):
    require_permission(request, Permission.MANAGE_PARTICIPANTS)
    logger.debug(
        'Fetching registration',
        extra={'tournament_id': id, 'registration_id': registration_pk},
    )
    registration = get_object_or_404(
        TournamentTeamRegistration.objects.select_related('team'),
        pk=registration_pk,
        tournament_id=id,
    )
    return _registration_response_data(registration)


@router.patch('/{id}/registrations/{registration_pk}/disqualification', operation_id='disqualifyTeamFromTournament', url_name='tournament_registration_disqualification', response={200: DisqualificationResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def disqualify_team_from_tournament(request, id: int, registration_pk: int, payload: DisqualificationRequest):
    require_permission(request, Permission.MANAGE_PARTICIPANTS)
    logger.info(
        'Disqualification action requested',
        extra={
            'tournament_id': id,
            'registration_id': registration_pk,
            'action': payload.action,
            'user_id': request.auth.id,
        },
    )
    registration = get_object_or_404(
        TournamentTeamRegistration.objects.select_related('team__captain', 'tournament')
        .prefetch_related('team__members'),
        pk=registration_pk,
        tournament_id=id,
    )
    if payload.action == 'disqualify':
        registration.is_active = False
        registration.is_disqualified = True
        registration.disqualification_reason = payload.disqualification_reason.strip() or 'Disqualified by admin'
        event_type = 'tournament_team_disqualified'
        action = 'disqualified'
    elif payload.action == 'reactivate':
        registration.is_active = True
        registration.is_disqualified = False
        registration.disqualification_reason = ''
        event_type = 'tournament_team_reactivated'
        action = 'activated'
    else:
        logger.warning(
            'Invalid disqualification action',
            extra={
                'registration_id': registration_pk,
                'action': payload.action,
                'user_id': request.auth.id,
            },
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'action must be "disqualify" or "reactivate".')

    registration.save(update_fields=['is_active', 'is_disqualified', 'disqualification_reason'])
    logger.info(
        'Team disqualification status changed',
        extra={
            'action': action,
            'team_id': registration.team_id,
            'tournament_id': registration.tournament_id,
            'registration_id': registration.id,
            'user_id': request.auth.id,
        },
    )
    NotificationService.notify(
        recipients=_team_participants(registration.team),
        event_type=event_type,
        context={
            'team_name': registration.team.name,
            'tournament_name': registration.tournament.name,
            'reason': registration.disqualification_reason or 'No reason provided',
        },
    )
    return {
        'id': registration.id,
        'team_id': registration.team_id,
        'team_name': registration.team.name,
        'tournament_id': registration.tournament_id,
        'is_active': registration.is_active,
        'action': action,
    }


@router.get('/{id}/my-submissions', operation_id='listMyTeamSubmissions', url_name='tournament_my_submissions', response={200: list[SubmissionResponse], 401: ErrorResponse, 404: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_my_team_submissions(request, id: int):
    logger.debug(
        'Listing my team submissions',
        extra={'tournament_id': id, 'user_id': request.auth.id},
    )
    tournament = get_object_or_404(Tournament, pk=id)
    registration = (
        TournamentTeamRegistration.objects.select_related('team')
        .filter(tournament=tournament, is_active=True)
        .filter(Q(team__captain_id=request.auth.id) | Q(team__team_members__user_id=request.auth.id))
        .first()
    )
    if registration is None:
        logger.warning(
            'No team participation found',
            extra={'tournament_id': id, 'user_id': request.auth.id},
        )
        raise_api_error(404, 'No team participation found for this tournament.')

    queryset = _submissions().filter(
        round__tournament=tournament,
        team_id=registration.team_id,
    ).order_by('-created_at', '-id')

    submissions = list(queryset)
    return [_submission_response_data(item, request) for item in submissions]


@router.get('/rounds/{id}/submissions', operation_id='listRoundSubmissions', url_name='round_submissions', response={200: list[SubmissionResponse], 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_round_submissions(request, id: int):
    logger.debug(
        'Listing round submissions',
        extra={'round_id': id, 'user_id': request.auth.id},
    )
    round_obj = get_object_or_404(Round, pk=id)
    queryset = (
        _submissions()
        .filter(round=round_obj)
        .order_by('-created_at', '-id')
        .exclude(
            team__tournament_registrations__tournament=round_obj.tournament,
            team__tournament_registrations__is_disqualified=True,
        )
    )
    submissions = list(queryset)
    return [_submission_response_data(item, request) for item in submissions]


@router.get('/my-calendar', operation_id='getMyCalendar', url_name="my_calendar", response={200: MyCalendarResponse, 401: ErrorResponse})
def get_my_calendar(request):
    logger.debug('Fetching calendar', extra={'user_id': request.auth.id})
    if has_permission(request.auth, Permission.VIEW_TOURNAMENT):
        tournament_ids = Tournament.objects.exclude(status=Tournament.STATUS_DRAFT).values_list('id', flat=True)
    else:
        tournament_ids = TournamentTeamRegistration.objects.filter(is_active=True).filter(
            Q(team__captain_id=request.auth.id) | Q(team__team_members__user_id=request.auth.id)
        ).values_list('tournament_id', flat=True)
    events = list(Event.objects.select_related('icon', 'tournament').filter(tournament_id__in=tournament_ids).order_by('start_datetime', 'id'))
    rounds = list(Round.objects.select_related('tournament').filter(tournament_id__in=tournament_ids).order_by('start_date', 'id'))
    return {
        'events': [
            {
                'id': event.id, 'tournament': event.tournament_id, 'type': event.type,
                'title': event.title, 'description': event.description, 'link': event.link,
                'start_datetime': event.start_datetime, 'icon': event.icon_id,
                'created_at': event.created_at, 'updated_at': event.updated_at,
            }
            for event in events
        ],
        'rounds': [
            {
                'id': round_obj.id, 'tournament': round_obj.tournament_id, 'name': round_obj.name,
                'description': round_obj.description, 'tech_requirements': round_obj.tech_requirements,
                'must_have_requirements': round_obj.must_have_requirements,
                'criteria': _criteria_data(round_obj.criteria), 'start_date': round_obj.start_date,
                'end_date': round_obj.end_date, 'passing_count': round_obj.passing_count,
                'evaluation_criteria': round_obj.evaluation_criteria, 'materials': round_obj.materials,
                'status': round_obj.status,
            }
            for round_obj in rounds
        ],
    }

@router.post('/my-calendar/export-to-google', operation_id='exportToGoogleCalendar', url_name='export_to_google_calendar', response={200: ExportToGoogleCalendarResponse, 400: ErrorResponse, 401: ErrorResponse})
def export_to_google_calendar(request, payload: ExportToGoogleCalendarRequest):
    logger.info(
        'Google Calendar export requested',
        extra={
            'user_id': request.auth.id,
            'event_count': len(payload.event_ids or []),
            'round_count': len(payload.round_ids or []),
        },
    )
    if not request.auth.google_calendar_connected:
        logger.warning('Google Calendar not connected', extra={'user_id': request.auth.id})
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Google Calendar is not connected. Please connect first.')
    service = get_calendar_service(request.auth)
    if not service:
        logger.error('Failed to build Google Calendar service', extra={'user_id': request.auth.id})
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Failed to connect to Google Calendar. Please reconnect.')
    if not payload.event_ids and not payload.round_ids:
        logger.warning('Google Calendar export with no IDs', extra={'user_id': request.auth.id})
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Provide event_ids or round_ids to export.')

    created = []
    errors = []
    for event in Event.objects.filter(id__in=payload.event_ids).select_related('tournament'):
        try:
            calendar_event = {
                'summary': f'{event.title} - {event.tournament.name}',
                'description': event.description or '',
                'start': {'dateTime': event.start_datetime.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': (event.start_datetime + timedelta(hours=1)).isoformat(), 'timeZone': 'UTC'},
            }
            if event.link:
                calendar_event['description'] += f'\n\nLink: {event.link}'
            result = service.events().insert(calendarId='primary', body=calendar_event).execute()
            created.append({'type': 'event', 'id': event.id, 'google_event_id': result.get('id'), 'html_link': result.get('htmlLink')})
        except Exception as error:
            logger.exception(
                'Failed to export event to Google Calendar',
                extra={'event_id': event.id, 'user_id': request.auth.id},
            )
            errors.append({'type': 'event', 'id': event.id, 'error': str(error)})
    for round_obj in Round.objects.filter(id__in=payload.round_ids).select_related('tournament'):
        try:
            start_event = {
                'summary': f'{round_obj.name} starts - {round_obj.tournament.name}',
                'description': f'Round starts for tournament {round_obj.tournament.name}',
                'start': {'dateTime': round_obj.start_date.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': (round_obj.start_date + timedelta(hours=1)).isoformat(), 'timeZone': 'UTC'},
            }
            deadline_event = {
                'summary': f'{round_obj.name} deadline - {round_obj.tournament.name}',
                'description': f'Submission deadline for {round_obj.name}',
                'start': {'dateTime': round_obj.end_date.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': (round_obj.end_date + timedelta(minutes=30)).isoformat(), 'timeZone': 'UTC'},
            }
            start_result = service.events().insert(calendarId='primary', body=start_event).execute()
            deadline_result = service.events().insert(calendarId='primary', body=deadline_event).execute()
            created.append({'type': 'round', 'id': round_obj.id, 'google_event_ids': [start_result.get('id'), deadline_result.get('id')]})
        except Exception as error:
            logger.exception(
                'Failed to export round to Google Calendar',
                extra={'round_id': round_obj.id, 'user_id': request.auth.id},
            )
            errors.append({'type': 'round', 'id': round_obj.id, 'error': str(error)})
    logger.info(
        'Google Calendar export finished',
        extra={
            'user_id': request.auth.id,
            'created_count': len(created),
            'error_count': len(errors),
        },
    )
    return {'created': created, 'errors': errors}


@router.get('', operation_id='listTournaments', url_name='tournaments', response={200: TournamentListResponse, 400: ErrorResponse})
def list_tournaments(request, page: int = 1, page_size: int = 20, searchQuery: str | None = None, status: str | None = None):
    sync_time_based_statuses()

    if page < 1 or page_size < 1:
        logger.warning(
            'Invalid pagination',
            extra={'page': page, 'page_size': page_size},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'page and page_size must be positive integers.')

    logger.debug(
        'Listing tournaments',
        extra={
            'page': page,
            'page_size': page_size,
            'search': searchQuery,
            'status': status,
        },
    )

    queryset = _visible_tournaments(request)
    if searchQuery:
        queryset = queryset.filter(Q(name__icontains=searchQuery) | Q(description__icontains=searchQuery))
    if status:
        requested_statuses = [item.strip() for item in status.split(',') if item.strip()]
        allowed_statuses = {value for value, _label in Tournament.STATUS_CHOICES}
        if not requested_statuses or not set(requested_statuses).issubset(allowed_statuses):
            raise_api_error(HTTPStatus.BAD_REQUEST, 'Invalid tournament status filter.')
        queryset = queryset.filter(status__in=requested_statuses)

    total = queryset.count()
    size = min(page_size, 100)
    page_items = list(queryset[(page - 1) * size:page * size])

    # Resolve the user's teams once for the whole page instead of once per row.
    team_ids = _registered_team_ids(getattr(request, 'auth', None))

    return {
        'data': [
            _tournament_response_data(tournament, request, team_ids)
            for tournament in page_items
        ],
        'total': total,
    }


@router.get(
    '/archive',
    operation_id='listTournamentArchive',
    url_name='tournament_archive_list',
    response={200: list[TournamentArchiveListResponse], 401: ErrorResponse},
)
@paginate(APIPageNumberPagination)
def list_tournament_archive(request):
    logger.debug('Listing tournament archive')
    tournaments = list(
        Tournament.objects.filter(status=Tournament.STATUS_FINISHED)
        .prefetch_related(
            'rounds',
            Prefetch(
                'leaderboard_entries',
                queryset=LeaderboardEntry.objects.filter(round__isnull=True)
                .select_related('team').order_by('rank'),
            ),
        )
        .order_by('id')
    )
    return [_archive_base_response_data(tournament, request) for tournament in tournaments]


@router.get(
    '/archive/{id}',
    operation_id='getTournamentArchive',
    url_name='tournament_archive_detail',
    response={200: TournamentArchiveDetailResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def get_tournament_archive(request, id: int):
    logger.debug('Fetching tournament archive', extra={'tournament_id': id})
    tournament = get_object_or_404(
        Tournament.objects.prefetch_related(
            'rounds',
            Prefetch('leaderboard_entries', queryset=LeaderboardEntry.objects.filter(
                round__isnull=True
            ).select_related('team').order_by('rank')),
            Prefetch('team_registrations', queryset=TournamentTeamRegistration.objects.filter(
                is_active=True
            ).select_related('team').order_by('team__name')),
        ),
        pk=id,
        status=Tournament.STATUS_FINISHED,
    )
    response_data = _archive_base_response_data(tournament, request)
    response_data['teams'] = [
        _team_summary_response_data(registration.team)
        for registration in tournament._prefetched_objects_cache.get('team_registrations', [])
    ]
    response_data['rounds'] = [
        _round_short_response_data(round_obj)
        for round_obj in tournament._prefetched_objects_cache.get('rounds', [])
    ]
    return response_data


@router.get('/archive/{id}/submissions', operation_id='listTournamentArchiveSubmissions', url_name='tournament_archive_submissions', response={200: list[SubmissionResponse], 401: ErrorResponse, 404: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_tournament_archive_submissions(request, id: int):
    logger.debug('Listing archive submissions', extra={'tournament_id': id})
    get_object_or_404(Tournament, pk=id, status=Tournament.STATUS_FINISHED)
    queryset = _submissions().filter(round__tournament_id=id).order_by('-created_at', '-id')

    submissions = list(queryset)
    return [_submission_response_data(item, request) for item in submissions]


@router.get('/{int:id}', operation_id='getTournament', url_name='tournament_detail', response={200: TournamentResponse, 404: ErrorResponse})
def get_tournament(request, id: int):
    logger.debug('Fetching tournament', extra={'tournament_id': id})
    tournament = get_object_or_404(_visible_tournaments(request), pk=id)

    return _tournament_response_data(tournament, request)

@router.post('/manage', operation_id='createTournament', url_name='tournament_manage_create', response={201: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_tournament(request, payload: TournamentCreateRequest):
    require_permission(request, Permission.CREATE_TOURNAMENT)
    tournament = _validate_model(Tournament(created_by=request.auth, **payload.model_dump()))
    tournament.save()
    logger.info(
        'Tournament created',
        extra={'tournament_id': tournament.id, 'user_id': request.auth.id},
    )

    return 201, _tournament_response_data(tournament, request)


@router.get('/manage/{id}', operation_id='getTournamentForUpdate', url_name='tournament_manage_update', response={200: TournamentResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_tournament_for_update(request, id: int):
    require_permission(request, Permission.VIEW_TOURNAMENT)
    logger.debug(
        'Fetching tournament for update',
        extra={'tournament_id': id, 'user_id': request.auth.id},
    )
    tournament = get_object_or_404(Tournament, pk=id)

    return _tournament_response_data(tournament, request)


def _save_tournament(request, pk, payload):
    require_permission(request, Permission.EDIT_TOURNAMENT)

    values = payload.model_dump(exclude_unset=True)
    tournament = _update_model(get_object_or_404(Tournament, pk=pk), values)
    tournament.save()
    logger.info(
        'Tournament updated',
        extra={
            'tournament_id': pk,
            'user_id': request.auth.id,
            'fields': sorted(values.keys()),
        },
    )

    return tournament


@router.patch('/manage/{id}', operation_id='updateTournament', url_name='tournament_manage_update', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_tournament(request, id: int, payload: TournamentUpdateRequest):
    tournament =_save_tournament(request, id, payload)

    return _tournament_response_data(tournament, request)


@router.delete('/manage/{id}', operation_id='deleteTournament', url_name='tournament_manage_update', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_tournament(request, id: int):
    require_permission(request, Permission.DELETE_TOURNAMENT)
    get_object_or_404(Tournament, pk=id).delete()
    logger.info(
        'Tournament deleted',
        extra={'tournament_id': id, 'user_id': request.auth.id},
    )

    return 204, None


@router.post('/{id}/start-registration', operation_id='startTournamentRegistration', url_name='tournament_start_registration', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def start_tournament_registration(request, id: int):
    require_permission(request, Permission.EDIT_TOURNAMENT)
    logger.info(
        'Starting registration',
        extra={'tournament_id': id, 'user_id': request.auth.id},
    )

    try:
        tournament = start_registration(get_object_or_404(Tournament, pk=id))
    except ValidationError as error:
        _validation_error(error)
    logger.info(
        'Registration started',
        extra={'tournament_id': id, 'status': tournament.status},
    )

    return _tournament_response_data(tournament, request)


@router.post('/{id}/register-team', operation_id='registerTeamForTournament', url_name='tournament_register_team', response={201: TeamRegistrationResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def register_team(request, id: int, payload: TeamRegistrationRequest):
    logger.info(
        'Team registration requested',
        extra={'tournament_id': id, 'team_id': payload.team_id, 'user_id': request.auth.id},
    )
    tournament = get_object_or_404(Tournament, pk=id)
    team = get_object_or_404(Team, pk=payload.team_id)

    try:
        registration = register_team_for_tournament(tournament=tournament, team=team, actor=request.auth)
    except ValidationError as error:
        _validation_error(error)
    logger.info(
        'Team registered',
        extra={
            'tournament_id': id,
            'team_id': team.id,
            'registration_id': registration.id,
            'user_id': request.auth.id,
        },
    )

    NotificationService.notify(
        recipients=_participants(tournament),
        event_type='tournament_team_registered',
        context={
            'team_name': team.name,
            'tournament_name': tournament.name,
        },
    )
    registration = TournamentTeamRegistration.objects.select_related('team').get(pk=registration.pk)
    return 201, _registration_response_data(registration)


@router.post('/{id}/leave-team', operation_id='unregisterTeamFromTournament', url_name='tournament_leave_team', response={200: TeamRegistrationResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def leave_team(request, id: int, payload: TeamRegistrationRequest):
    logger.info(
        'Team leave requested',
        extra={'tournament_id': id, 'team_id': payload.team_id, 'user_id': request.auth.id},
    )
    tournament = get_object_or_404(Tournament, pk=id)
    team = get_object_or_404(Team, pk=payload.team_id)

    try:
        registration = leave_team_from_tournament(tournament=tournament, team=team, actor=request.auth)
    except ValidationError as error:
        _validation_error(error)
    logger.info(
        'Team left tournament',
        extra={
            'tournament_id': id,
            'team_id': team.id,
            'registration_id': registration.id,
            'user_id': request.auth.id,
        },
    )

    registration = TournamentTeamRegistration.objects.select_related('team').get(pk=registration.pk)
    return _registration_response_data(registration)


@router.get('/{id}/eligible-teams', operation_id='listEligibleTeamsForTournament', url_name='tournament_eligible_teams', response={200: list[EligibleTeamResponse], 401: ErrorResponse, 404: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_eligible_teams(request, id: int):
    logger.debug(
        'Listing eligible teams',
        extra={'tournament_id': id, 'user_id': request.auth.id},
    )
    tournament = get_object_or_404(Tournament, pk=id)
    teams = list(
        Team.objects.filter(captain_id=request.auth.id).order_by('id')
        .annotate(members_count=Count('team_members', distinct=True))
        .prefetch_related('team_members')
    )
    team_ids = [team.id for team in teams]
    participant_ids_by_team = {
        team.id: {team.captain_id, *(member.user_id for member in team.team_members.all())}
        for team in teams
    }
    participant_ids = {
        participant_id
        for team_participant_ids in participant_ids_by_team.values()
        for participant_id in team_participant_ids
    }

    active_registrations = list(
        TournamentTeamRegistration.objects.filter(
            team_id__in=team_ids,
            is_active=True,
            tournament__status__in=[Tournament.STATUS_REGISTRATION, Tournament.STATUS_RUNNING],
        ).values_list('team_id', 'tournament_id')
    )
    active_team_ids = {
        team_id for team_id, tournament_id in active_registrations if tournament_id == id
    }
    teams_in_other_tournaments = {
        team_id for team_id, tournament_id in active_registrations if tournament_id != id
    }
    conflicting_member_ids = set(
        TeamMember.objects.filter(
            user_id__in=participant_ids,
            team__tournament_registrations__is_active=True,
            team__tournament_registrations__tournament__status__in=[
                Tournament.STATUS_REGISTRATION,
                Tournament.STATUS_RUNNING,
            ],
        )
        .exclude(team_id__in=team_ids)
        .values_list('user_id', flat=True)
    )
    tournament_is_full = (
        tournament.max_teams is not None
        and TournamentTeamRegistration.objects.filter(tournament=tournament, is_active=True).count()
        >= tournament.max_teams
    )

    responses = []
    for team in teams:
        reason = None
        if tournament.status != Tournament.STATUS_REGISTRATION:
            reason = 'Tournament is not open for team registration.'
        elif team.id in active_team_ids:
            reason = 'This team is already registered for the tournament.'
        elif (
            tournament.min_team_members
            and len(participant_ids_by_team[team.id]) < tournament.min_team_members
        ):
            reason = f'Team must have at least {tournament.min_team_members} members for this tournament.'
        elif tournament_is_full:
            reason = 'Tournament registration limit has been reached.'
        elif team.id in teams_in_other_tournaments:
            reason = 'This team is already participating in another tournament.'
        elif participant_ids_by_team[team.id] & conflicting_member_ids:
            reason = 'One or more team members are already participating in another tournament.'

        responses.append({
            'id': team.id,
            'name': team.name,
            'members_count': team.members_count,
            'reason': reason,
        })

    return responses


@router.get('/{id}/teams', operation_id='listTournamentTeams', url_name='tournament_teams', response={200: list[TournamentTeamResponse], 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_tournament_teams(request, id: int, status: str = 'active'):
    logger.debug(
        'Listing tournament teams',
        extra={'tournament_id': id, 'status': status},
    )
    if status not in {'active', 'all', 'disqualified'}:
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Invalid team registration status filter.')
    get_object_or_404(Tournament, pk=id)
    queryset = TournamentTeamRegistration.objects.filter(tournament_id=id).select_related('team', 'team__captain').prefetch_related('team__members').order_by('id')

    if status == 'disqualified':
        queryset = queryset.filter(is_disqualified=True)
    elif status != 'all':
        queryset = queryset.filter(is_active=True)

    registrations = list(queryset)
    return [_tournament_team_response_data(item, request) for item in registrations]


@router.get('/active', operation_id='getTeamActiveTournament', url_name='team_active_tournament', response={200: ActiveTournamentResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_active_tournament(request, team_id: int):
    logger.debug(
        'Fetching active tournament',
        extra={'team_id': team_id, 'user_id': request.auth.id},
    )
    registration = TournamentTeamRegistration.objects.select_related('tournament').filter(team_id=team_id, is_active=True, tournament__status__in=[Tournament.STATUS_REGISTRATION, Tournament.STATUS_RUNNING]).first()

    if registration is None:
        logger.info('No active tournament for team', extra={'team_id': team_id})
        raise_api_error(HTTPStatus.NOT_FOUND, 'Active tournament not found for this team.')

    tournament = registration.tournament
    return {
        'id': tournament.id,
        'name': tournament.name,
        'status': tournament.status,
        'start_date': tournament.start_date,
    }


@router.get('/{tournament_pk}/rounds', operation_id='listRounds', url_name='rounds', response={200: list[RoundResponse], 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_rounds(request, tournament_pk: int, status: str | None = None):
    logger.debug(
        'Listing rounds',
        extra={'tournament_id': tournament_pk, 'status': status},
    )
    tournament = get_object_or_404(Tournament, pk=tournament_pk)
    queryset = _rounds().filter(tournament=tournament)

    if not has_permission(request.auth, Permission.VIEW_TOURNAMENT):
        queryset = queryset.exclude(status=Round.STATUS_DRAFT)
    if status:
        requested_statuses = [item.strip() for item in status.split(',') if item.strip()]
        allowed_statuses = {value for value, _label in Round.STATUS_CHOICES}
        if not requested_statuses or not set(requested_statuses).issubset(allowed_statuses):
            raise_api_error(HTTPStatus.BAD_REQUEST, 'Invalid round status filter.')
        queryset = queryset.filter(status__in=requested_statuses)

    rounds = list(queryset)
    return [_round_response_data(item) for item in rounds]


@router.post('/{tournament_pk}/rounds', operation_id='createRound', url_name='rounds', response={201: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def create_round(request, tournament_pk: int, payload: RoundCreateRequest):
    require_permission(request, Permission.MANAGE_ROUNDS)

    tournament = get_object_or_404(Tournament, pk=tournament_pk)
    data = payload.model_dump()
    data['criteria'] = _criteria_data(data['criteria'])

    round_obj = _validate_model(Round(tournament=tournament, **data))
    round_obj.save()
    logger.info(
        'Round created',
        extra={
            'round_id': round_obj.id,
            'tournament_id': tournament_pk,
            'user_id': request.auth.id,
        },
    )

    return 201, _round_response_data(round_obj)


@router.get('/rounds/{id}', operation_id='getRound', url_name='round_detail', response={200: RoundResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_round(request, id: int):
    logger.debug('Fetching round', extra={'round_id': id})
    round_obj = get_object_or_404(_rounds(), pk=id)

    return _round_response_data(round_obj)


def _save_round(request, pk, payload):
    require_permission(request, Permission.MANAGE_ROUNDS)
    values = payload.model_dump(exclude_unset=True)

    if 'criteria' in values and values['criteria'] is not None:
        values['criteria'] = _criteria_data(values['criteria'])

    round_obj = _update_model(get_object_or_404(_rounds(), pk=pk), values)
    round_obj.save()
    logger.info(
        'Round updated',
        extra={
            'round_id': pk,
            'user_id': request.auth.id,
            'fields': sorted(values.keys()),
        },
    )

    return round_obj


@router.patch('/rounds/{id}', operation_id='updateRound', url_name='round_detail', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_round(request, id: int, payload: RoundUpdateRequest):
    return _round_response_data(_save_round(request, id, payload))


@router.delete('/rounds/{id}', operation_id='deleteRound', url_name='round_detail', response={204: None, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_round_view(request, id: int):
    require_permission(request, Permission.MANAGE_ROUNDS)
    logger.info('Deleting round', extra={'round_id': id, 'user_id': request.auth.id})

    try:
        delete_round(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    logger.info('Round deleted', extra={'round_id': id, 'user_id': request.auth.id})

    return 204, None


@router.post('/rounds/{id}/start', operation_id='startRound', url_name='round_start', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def start_round_view(request, id: int):
    require_permission(request, Permission.MANAGE_ROUNDS)
    logger.info('Starting round', extra={'round_id': id, 'user_id': request.auth.id})

    try:
        round_obj = start_round(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    logger.info('Round started', extra={'round_id': id, 'status': round_obj.status})

    return _round_response_data(round_obj)


@router.post('/rounds/{id}/close-submissions', url_name='round_close_submissions', operation_id='closeRoundSubmissions', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def close_round_submissions(request, id: int):
    require_permission(request, Permission.MANAGE_ROUNDS)
    logger.info('Closing round submissions', extra={'round_id': id, 'user_id': request.auth.id})

    try:
        round_obj = close_submissions_on_round(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    logger.info('Round submissions closed', extra={'round_id': id, 'status': round_obj.status})

    return _round_response_data(round_obj)


@router.post('/rounds/{id}/mark-evaluated', operation_id='markRoundEvaluated', url_name='round_mark_evaluated', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def mark_round_evaluated_view(request, id: int):
    require_permission(request, Permission.MANAGE_ROUNDS)
    logger.info('Marking round evaluated', extra={'round_id': id, 'user_id': request.auth.id})

    try:
        round_obj = mark_round_evaluated(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    logger.info('Round marked evaluated', extra={'round_id': id, 'status': round_obj.status})

    return _round_response_data(round_obj)


@router.get('/submissions', operation_id='listSubmissions', url_name='submissions', response={200: list[OwnSubmissionResponse], 401: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_submissions(request):
    logger.debug('Listing own submissions', extra={'user_id': request.auth.id})
    queryset = _submissions().filter(
        Q(team__captain_id=request.auth.id) | Q(team__team_members__user_id=request.auth.id)
    ).distinct().order_by('-created_at', '-id')

    submissions = list(queryset)
    return [_own_submission_response_data(item, request) for item in submissions]


@router.post('/submissions', operation_id='createSubmission', url_name="submissions", response={201: SubmissionResponse, 400: ErrorResponse, 401: ErrorResponse})
def create_submission(request, payload: SubmissionCreateRequest):
    logger.info(
        'Creating submission',
        extra={'round_id': payload.round, 'user_id': request.auth.id},
    )
    round_obj = get_object_or_404(Round.objects.select_related('tournament'), pk=payload.round)
    team = Team.objects.filter(captain=request.auth).filter(tournament_registrations__tournament=round_obj.tournament, tournament_registrations__is_active=True).first()

    if team is None:
        logger.warning(
            'Submission rejected, user is not captain of an active registered team',
            extra={
                'round_id': round_obj.id,
                'tournament_id': round_obj.tournament_id,
                'user_id': request.auth.id,
            },
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Only team captain can create submissions for an active registered team in this tournament.')
    submission = Submission(team=team, round=round_obj, created_by=request.auth, **payload.model_dump(exclude={'round'}))

    _validate_model(submission)

    try:
        submission.save()
    except IntegrityError:
        logger.warning(
            'Submission rejected, duplicate',
            extra={
                'round_id': round_obj.id,
                'team_id': team.id,
                'user_id': request.auth.id,
            },
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Only one submission per team per round is allowed.')
    logger.info(
        'Submission created',
        extra={
            'submission_id': submission.id,
            'round_id': round_obj.id,
            'team_id': team.id,
            'user_id': request.auth.id,
        },
    )

    submission = _submissions().get(pk=submission.pk)
    return 201, _submission_response_data(submission, request)


@router.get('/submissions/{id}', operation_id='getSubmission', url_name='submission_detail', response={200: SubmissionResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_submission(request, id: int):
    logger.debug(
        'Fetching submission',
        extra={'submission_id': id, 'user_id': request.auth.id},
    )
    submission = get_object_or_404(_submissions().filter(team__captain_id=request.auth.id), pk=id)

    return _submission_response_data(submission, request)


def _save_submission(request, pk, payload):
    submission = get_object_or_404(_submissions(), pk=pk)

    if submission.team.captain_id != request.auth.id:
        logger.warning(
            'Submission update rejected, not captain',
            extra={
                'submission_id': pk,
                'user_id': request.auth.id,
                'captain_id': submission.team.captain_id,
            },
        )
        raise_api_error(
            HTTPStatus.BAD_REQUEST,
            "Only team captain can update submission",
            {
                "team": "Only team captain can update submission"
            }
        )

    values = payload.model_dump(exclude_unset=True)
    _update_model(submission, values)
    submission.save()
    logger.info(
        'Submission updated',
        extra={
            'submission_id': pk,
            'user_id': request.auth.id,
            'fields': sorted(values.keys()),
        },
    )

    submission = _submissions().get(pk=submission.pk)
    return _submission_response_data(submission, request)

@router.patch('/submissions/{id}', operation_id='updateSubmission', url_name='submission_detail', response={200: SubmissionResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def update_submission(request, id: int, payload: SubmissionUpdateRequest):
    return _save_submission(request, id, payload)


@router.get('/{id}/submissions', operation_id='listTournamentSubmissions', url_name='tournament_submissions',
            response={200: list[SubmissionResponse], 401: ErrorResponse, 404: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_tournament_submissions(request, id: int):
    logger.debug('Listing tournament submissions', extra={'tournament_id': id})
    tournament = get_object_or_404(Tournament, pk=id)

    disqualified_teams = TournamentTeamRegistration.objects.filter(
        tournament=tournament,
        is_disqualified=True,
    ).values('team_id')

    queryset = (
        _submissions()
        .filter(round__tournament=tournament)
        .exclude(team_id__in=disqualified_teams)
        .order_by('-created_at', '-id')
    )

    submissions = list(queryset)
    return [_submission_response_data(item, request) for item in submissions]


@router.get('/current-task', operation_id='getCurrentTask', url_name='current_task', response={200: CurrentTaskResponse | None, 401: ErrorResponse})
def get_current_task(request, tournament_id: int | None = None):
    logger.debug('Fetching current task', extra={'tournament_id': tournament_id})
    queryset = Round.objects.filter(
        status=Round.STATUS_ACTIVE,
        tournament__status=Tournament.STATUS_RUNNING,
    ).select_related('tournament').order_by('end_date', 'id')
    if tournament_id is not None:
        queryset = queryset.filter(tournament_id=tournament_id)

    round_obj = queryset.first()
    if round_obj is None:
        logger.info('No active task found', extra={'tournament_id': tournament_id})
        return None
    return {
        'id': round_obj.id,
        'tournament_id': round_obj.tournament_id,
        'tournament_name': round_obj.tournament.name,
        'name': round_obj.name,
        'task': round_obj.description,
        'deadline': round_obj.end_date,
        'must_have_requirements': round_obj.must_have_requirements,
        'tech_requirements': round_obj.tech_requirements,
    }


def _save_event(request, payload, instance=None):
    values = payload.model_dump(exclude_unset=True)
    if 'tournament' in values:
        values['tournament_id'] = values.pop('tournament')
    if 'icon' in values:
        values['icon_id'] = values.pop('icon')
    if instance is None:
        event = Event(**values)
    else:
        event = _update_model(instance, values)
    if event.type == Event.TYPE_EVENT:
        event.link = ''
    _validate_model(event)
    event.save()
    logger.info(
        'Event created' if instance is None else 'Event updated',
        extra={
            'event_id': event.id,
            'tournament_id': event.tournament_id,
            'user_id': request.auth.id,
        },
    )
    return event


@router.get('/events', operation_id='listEvents', url_name="event", response={200: list[EventResponse], 401: ErrorResponse})
@paginate(APIPageNumberPagination)
def list_events(request, tournament: int | None = None):
    logger.debug('Listing events', extra={'tournament_id': tournament})
    events = Event.objects.all()
    if tournament is not None:
        events = events.filter(tournament_id=tournament)

    events = list(events.order_by('id'))
    return [_event_response_data(event) for event in events]


@router.post('/events', operation_id='createEvent', url_name="event", response={201: EventResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_event(request, payload: EventCreateRequest):
    require_permission(request, Permission.MANAGE_EVENTS)
    event = _save_event(request, payload)
    return 201, _event_response_data(event)


@router.get('/events/{id}', operation_id='getEvent', url_name="event", response={200: EventResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_event(request, id: int):
    logger.debug('Fetching event', extra={'event_id': id})
    event = get_object_or_404(Event, pk=id)
    return _event_response_data(event)


@router.patch('/events/{id}', operation_id='updateEvent', url_name="event", response={200: EventResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_event(request, id: int, payload: EventUpdateRequest):
    require_permission(request, Permission.MANAGE_EVENTS)
    event = _save_event(request, payload, get_object_or_404(Event, pk=id))
    return _event_response_data(event)


@router.delete('/events/{id}', operation_id='deleteEvent', url_name="event", response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_event(request, id: int):
    require_permission(request, Permission.MANAGE_EVENTS)
    get_object_or_404(Event, pk=id).delete()
    logger.info('Event deleted', extra={'event_id': id, 'user_id': request.auth.id})

    return 204, None
