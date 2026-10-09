import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from ninja import File, Router
from ninja.files import UploadedFile

from accounts.models import User
from accounts.google_calendar import get_calendar_service
from backend.auth import JWTAuth
from backend.permissions import Permission, require_permission, has_permission
from backend.schemas import ErrorResponse
from evaluation.leaderboard_service import get_tournament_leaderboard
from notifications.services import NotificationService
from teams.models import Team

from .models import Event, Round, Submission, Tournament, TournamentTeamRegistration
from backend.errors import raise_api_error
from http import HTTPStatus
from .schemas import (
    ActiveTournamentResponse, CurrentTaskResponse, EligibleTeamResponse,
    CalendarEventResponse, CalendarRoundResponse, DisqualificationRequest, DisqualificationResponse, ExportToGoogleCalendarRequest,
    ExportToGoogleCalendarResponse, MyCalendarResponse,
    EventCreateRequest, EventListResponse, EventResponse, EventUpdateRequest, OwnSubmissionResponse,
    RoundCreateRequest, RoundResponse, RoundUpdateRequest,
    SubmissionCreateRequest,
    SubmissionListResponse, SubmissionResponse, SubmissionUpdateRequest, TeamRegistrationRequest,
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


def _get_registered_team(tournament, request):
    user = getattr(request, "auth", None)

    if not (user and getattr(user, "is_authenticated", False)):
        return None

    team_ids = set(user.teams.values_list("id", flat=True)) | set(
        Team.objects.filter(captain=user).values_list("id", flat=True)
    )

    registration = (
        tournament.team_registrations
        .filter(team_id__in=team_ids, is_active=True)
        .select_related("team")
        .first()
    )

    return registration.team if registration else None


def _attach_registered_team(tournament, request):
    # Whether the current user has a team registered is request-scoped (depends on
    # request.auth), so it can't be computed inside a schema resolver. We compute it
    # here and stash it on the instance; TournamentResponse.resolve_registered_team
    # just reads it back off.
    tournament._registered_team = _get_registered_team(tournament, request)
    return tournament


def _team_participants(team: Team) -> list[User]:
    participants = {team.captain_id: team.captain} if team.captain_id else {}
    participants.update({member.id: member for member in team.members.all()})
    return list(participants.values())


@router.patch('/manage/{id}/banner', operation_id='updateTournamentBanner', url_name='tournament_manage_banner', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_tournament_banner(request, id: int, banner: UploadedFile = File(...)):
    require_permission(request, Permission.EDIT_TOURNAMENT)
    tournament = get_object_or_404(Tournament, pk=id)

    tournament.banner = banner
    tournament.save(update_fields=['banner'])
    logger.info(
        'Tournament banner updated',
        extra={
            'tournament_id': id,
            'user_id': request.auth.id,
            'file_name': banner.name,
            'file_size': banner.size,
        },
    )

    registered_team = _get_registered_team(tournament, request)

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
        context={
            "registered_team": registered_team,
        },
    )


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

    registered_team = _get_registered_team(tournament, request)

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
        context={
            "registered_team": registered_team,
        },
    )


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
    return TeamRegistrationResponse.from_orm(registration)


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
    return DisqualificationResponse(
        id=registration.id,
        team_id=registration.team_id,
        team_name=registration.team.name,
        tournament_id=registration.tournament_id,
        is_active=registration.is_active,
        action=action,
    )


@router.get('/{id}/my-submissions', operation_id='listMyTeamSubmissions', url_name='tournament_my_submissions', response={200: SubmissionListResponse, 401: ErrorResponse, 404: ErrorResponse})
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

    queryset = _submissions().filter(round__tournament=tournament, team_id=registration.team_id)

    return SubmissionListResponse.model_construct(
        root=[
            SubmissionResponse.model_validate(
                submission,
                from_attributes=True,
            )
            for submission in queryset
        ]
    )


@router.get('/rounds/{id}/submissions', operation_id='listRoundSubmissions', url_name='round_submissions', response={200: SubmissionListResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def list_round_submissions(request, id: int):
    logger.debug(
        'Listing round submissions',
        extra={'round_id': id, 'user_id': request.auth.id},
    )
    round_obj = get_object_or_404(Round, pk=id)
    queryset = (
        _submissions()
        .filter(round=round_obj)
        .exclude(
            team__tournament_registrations__tournament=round_obj.tournament,
            team__tournament_registrations__is_disqualified=True,
        )
    )
    return SubmissionListResponse.model_construct(
        root=[
            SubmissionResponse.model_validate(
                submission,
                from_attributes=True,
            )
            for submission in queryset
        ]
    )


@router.get('/my-calendar', operation_id='getMyCalendar', url_name="my_calendar", response={200: MyCalendarResponse, 401: ErrorResponse})
def get_my_calendar(request):
    logger.debug('Fetching calendar', extra={'user_id': request.auth.id})
    if has_permission(request.auth, Permission.VIEW_TOURNAMENT):
        tournament_ids = Tournament.objects.exclude(status=Tournament.STATUS_DRAFT).values_list('id', flat=True)
    else:
        tournament_ids = TournamentTeamRegistration.objects.filter(is_active=True).filter(
            Q(team__captain_id=request.auth.id) | Q(team__team_members__user_id=request.auth.id)
        ).values_list('tournament_id', flat=True)
    events = Event.objects.select_related('icon', 'tournament').filter(tournament_id__in=tournament_ids).order_by('start_datetime')
    rounds = Round.objects.select_related('tournament').filter(tournament_id__in=tournament_ids).order_by('start_date')
    return MyCalendarResponse.model_construct(
        events=[CalendarEventResponse.from_orm(event) for event in events],
        rounds=[CalendarRoundResponse.from_orm(round_obj) for round_obj in rounds],
    )

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
    return ExportToGoogleCalendarResponse(created=created, errors=errors)


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
        queryset = queryset.filter(status__in=[item.strip() for item in status.split(',') if item.strip()])

    total = queryset.count()
    size = min(page_size, 100)
    page_items = queryset[(page - 1) * size:page * size]


    return TournamentListResponse.model_construct(
        data=[
            TournamentResponse.model_validate(
                _attach_registered_team(tournament, request),
                from_attributes=True,
            )
            for tournament in page_items
        ],
        total=total,
    )


@router.get(
    '/archive',
    operation_id='listTournamentArchive',
    url_name='tournament_archive_list',
    response={200: list[TournamentArchiveListResponse], 401: ErrorResponse},
)
def list_tournament_archive(request):
    logger.debug('Listing tournament archive')
    return Tournament.objects.filter(status=Tournament.STATUS_FINISHED)


@router.get(
    '/archive/{id}',
    operation_id='getTournamentArchive',
    url_name='tournament_archive_detail',
    response={200: TournamentArchiveDetailResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def get_tournament_archive(request, id: int):
    logger.debug('Fetching tournament archive', extra={'tournament_id': id})
    return get_object_or_404(Tournament, pk=id, status=Tournament.STATUS_FINISHED)


@router.get('/archive/{id}/submissions', operation_id='listTournamentArchiveSubmissions', url_name='tournament_archive_submissions', response={200: SubmissionListResponse, 401: ErrorResponse, 404: ErrorResponse})
def list_tournament_archive_submissions(request, id: int):
    logger.debug('Listing archive submissions', extra={'tournament_id': id})
    get_object_or_404(Tournament, pk=id, status=Tournament.STATUS_FINISHED)
    queryset = _submissions().filter(round__tournament_id=id)

    return SubmissionListResponse.model_construct(
        root=[
            SubmissionResponse.model_validate(
                submission,
                from_attributes=True,
            )
            for submission in queryset
        ]
    )


@router.get('/{int:id}', operation_id='getTournament', url_name='tournament_detail', response={200: TournamentResponse, 404: ErrorResponse})
def get_tournament(request, id: int):
    logger.debug('Fetching tournament', extra={'tournament_id': id})
    tournament = get_object_or_404(_visible_tournaments(request), pk=id)

    registered_team = _get_registered_team(tournament, request)

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
        context={
            "registered_team": registered_team,
        },
    )

@router.post('/manage', operation_id='createTournament', url_name='tournament_manage_create', response={201: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_tournament(request, payload: TournamentCreateRequest):
    require_permission(request, Permission.CREATE_TOURNAMENT)
    tournament = _validate_model(Tournament(created_by=request.auth, **payload.model_dump()))
    tournament.save()
    logger.info(
        'Tournament created',
        extra={'tournament_id': tournament.id, 'user_id': request.auth.id},
    )

    registered_team = _get_registered_team(tournament, request)

    return 201, TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
        context={
            "registered_team": registered_team,
        },
    )


@router.get('/manage/{id}', operation_id='getTournamentForUpdate', url_name='tournament_manage_update', response={200: TournamentResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_tournament_for_update(request, id: int):
    require_permission(request, Permission.VIEW_TOURNAMENT)
    logger.debug(
        'Fetching tournament for update',
        extra={'tournament_id': id, 'user_id': request.auth.id},
    )
    tournament = get_object_or_404(Tournament, pk=id)

    registered_team = _get_registered_team(tournament, request)

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
        context={
            "registered_team": registered_team,
        },
    )


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

    registered_team = _get_registered_team(tournament, request)

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
        context={
            "registered_team": registered_team,
        },
    )


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

    registered_team = _get_registered_team(tournament, request)

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
        context={
            "registered_team": registered_team,
        },
    )


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

    NotificationService.notify(recipients=_participants(tournament), event_type='tournament_team_registered', context={'team_name': team.name, 'tournament_name': tournament.name})
    return 201, TeamRegistrationResponse.model_validate(registration, from_attributes=True)


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

    return TeamRegistrationResponse.model_validate(registration, from_attributes=True)


@router.get('/{id}/eligible-teams', operation_id='listEligibleTeamsForTournament', url_name='tournament_eligible_teams', response={200: list[EligibleTeamResponse], 401: ErrorResponse, 404: ErrorResponse})
def list_eligible_teams(request, id: int):
    logger.debug(
        'Listing eligible teams',
        extra={'tournament_id': id, 'user_id': request.auth.id},
    )
    get_object_or_404(Tournament, pk=id)
    queryset = Team.objects.filter(captain_id=request.auth.id).annotate(members_count=Count('team_members', distinct=True))

    return [EligibleTeamResponse.model_validate(team, from_attributes=True) for team in queryset]


@router.get('/{id}/teams', operation_id='listTournamentTeams', url_name='tournament_teams', response={200: list[TournamentTeamResponse], 401: ErrorResponse, 404: ErrorResponse})
def list_tournament_teams(request, id: int, status: str = 'active'):
    logger.debug(
        'Listing tournament teams',
        extra={'tournament_id': id, 'status': status},
    )
    get_object_or_404(Tournament, pk=id)
    queryset = TournamentTeamRegistration.objects.filter(tournament_id=id).select_related('team', 'team__captain').prefetch_related('team__members')

    if status == 'disqualified':
        queryset = queryset.filter(is_disqualified=True)
    elif status != 'all':
        queryset = queryset.filter(is_active=True)

    return queryset


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

    return ActiveTournamentResponse.model_validate(registration.tournament, from_attributes=True)


@router.get('/{tournament_pk}/rounds', operation_id='listRounds', url_name='rounds', response={200: list[RoundResponse], 401: ErrorResponse, 404: ErrorResponse})
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
        queryset = queryset.filter(status__in=[item.strip() for item in status.split(',') if item.strip()])

    return queryset


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

    return 201, round_obj


@router.get('/rounds/{id}', operation_id='getRound', url_name='round_detail', response={200: RoundResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_round(request, id: int):
    logger.debug('Fetching round', extra={'round_id': id})
    round_obj = get_object_or_404(_rounds(), pk=id)

    return round_obj


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
    return _save_round(request, id, payload)


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

    return round_obj


@router.post('/rounds/{id}/close-submissions', url_name='round_close_submissions', operation_id='closeRoundSubmissions', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def close_round_submissions(request, id: int):
    require_permission(request, Permission.MANAGE_ROUNDS)
    logger.info('Closing round submissions', extra={'round_id': id, 'user_id': request.auth.id})

    try:
        round_obj = close_submissions_on_round(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    logger.info('Round submissions closed', extra={'round_id': id, 'status': round_obj.status})

    return round_obj


@router.post('/rounds/{id}/mark-evaluated', operation_id='markRoundEvaluated', url_name='round_mark_evaluated', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def mark_round_evaluated_view(request, id: int):
    require_permission(request, Permission.MANAGE_ROUNDS)
    logger.info('Marking round evaluated', extra={'round_id': id, 'user_id': request.auth.id})

    try:
        round_obj = mark_round_evaluated(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    logger.info('Round marked evaluated', extra={'round_id': id, 'status': round_obj.status})

    return round_obj


@router.get('/submissions', operation_id='listSubmissions', url_name='submissions', response={200: list[OwnSubmissionResponse], 401: ErrorResponse})
def list_submissions(request):
    logger.debug('Listing own submissions', extra={'user_id': request.auth.id})
    queryset = _submissions().filter(
        Q(team__captain_id=request.auth.id) | Q(team__team_members__user_id=request.auth.id)
    ).distinct()

    return queryset


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

    return 201, _submissions().get(pk=submission.pk)


@router.get('/submissions/{id}', operation_id='getSubmission', url_name='submission_detail', response={200: SubmissionResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_submission(request, id: int):
    logger.debug(
        'Fetching submission',
        extra={'submission_id': id, 'user_id': request.auth.id},
    )
    submission = get_object_or_404(_submissions().filter(team__captain_id=request.auth.id), pk=id)

    return submission


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

    return _submissions().get(pk=submission.pk)

@router.patch('/submissions/{id}', operation_id='updateSubmission', url_name='submission_detail', response={200: SubmissionResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def update_submission(request, id: int, payload: SubmissionUpdateRequest):
    return _save_submission(request, id, payload)


@router.get('/{id}/submissions', operation_id='listTournamentSubmissions', url_name='tournament_submissions',
            response={200: SubmissionListResponse, 401: ErrorResponse, 404: ErrorResponse})
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
    )

    return SubmissionListResponse.model_construct(
        root=[
            SubmissionResponse.model_validate(submission, from_attributes=True)
            for submission in queryset
        ]
    )


@router.get('/current-task', operation_id='getCurrentTask', url_name='current_task', response={200: CurrentTaskResponse, 401: ErrorResponse, 404: ErrorResponse})
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
        raise_api_error(404, 'No active task found.')
    return CurrentTaskResponse.model_validate(round_obj, from_attributes=True)


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


@router.get('/events', operation_id='listEvents', url_name="event", response={200: EventListResponse, 401: ErrorResponse})
def list_events(request, tournament: int | None = None):
    logger.debug('Listing events', extra={'tournament_id': tournament})
    events = Event.objects.all()
    if tournament is not None:
        events = events.filter(tournament_id=tournament)

    return EventListResponse.model_construct(root=[
        EventResponse.model_validate(event, from_attributes=True)
        for event in events
    ])


@router.post('/events', operation_id='createEvent', url_name="event", response={201: EventResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_event(request, payload: EventCreateRequest):
    require_permission(request, Permission.MANAGE_EVENTS)
    return 201, EventResponse.model_validate(_save_event(request, payload), from_attributes=True)


@router.get('/events/{id}', operation_id='getEvent', url_name="event", response={200: EventResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_event(request, id: int):
    logger.debug('Fetching event', extra={'event_id': id})
    event = get_object_or_404(Event, pk=id)
    return EventResponse.model_validate(event, from_attributes=True)


@router.patch('/events/{id}', operation_id='updateEvent', url_name="event", response={200: EventResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_event(request, id: int, payload: EventUpdateRequest):
    require_permission(request, Permission.MANAGE_EVENTS)
    return EventResponse.model_validate(_save_event(request, payload, get_object_or_404(Event, pk=id)), from_attributes=True)


@router.delete('/events/{id}', operation_id='deleteEvent', url_name="event", response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_event(request, id: int):
    require_permission(request, Permission.MANAGE_EVENTS)
    get_object_or_404(Event, pk=id).delete()
    logger.info('Event deleted', extra={'event_id': id, 'user_id': request.auth.id})

    return 204, None