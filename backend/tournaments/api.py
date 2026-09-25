from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from ninja import File, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile

from accounts.models import User
from accounts.google_calendar import _get_calendar_service
from backend.auth import JWTAuth
from backend.permissions import Permission, has_permission
from backend.schemas import ErrorResponse
from certificates.models import Certificate, CertificateTemplate
from evaluation.leaderboard_service import get_tournament_leaderboard
from notifications.services import NotificationService
from teams.models import Team

from .models import Event, Icon, Round, Submission, Tournament, TournamentTeamRegistration
from .schemas import (
    ActiveTournamentResponse, ArchiveStandingResponse, CriterionResponse, CurrentTaskResponse, EligibleTeamResponse,
    CalendarEventResponse, CalendarExportErrorResponse, CalendarRoundResponse, DisqualificationRequest, DisqualificationResponse, ExportToGoogleCalendarRequest,
    ExportToGoogleCalendarResponse, MyCalendarResponse,
    EventCreateRequest, EventListResponse, EventResponse, EventUpdateRequest, IconResponse, OwnSubmissionResponse,
    RoundCreateRequest, RoundResponse, RoundShortResponse, RoundUpdateRequest,
    SubmissionAssignmentResponse, SubmissionCreateRequest, SubmissionEvaluationResponse,
    SubmissionListResponse, SubmissionResponse, SubmissionUpdateRequest, TeamMemberResponse, TeamRegistrationRequest,
    TeamRegistrationResponse, TeamSummaryResponse, TournamentArchiveDetailResponse,
    TournamentArchiveListResponse, TournamentCreateRequest, TournamentListResponse,
    TournamentCertificateDeliveryStatusResponse, TournamentResponse, TournamentTeamResponse, TournamentUpdateRequest,
    RoundShortResponse, SendTournamentCertificatesRequest, SendTournamentCertificatesResponse,
)
from .services import (
    close_submissions_on_round, delete_round, leave_team_from_tournament,
    mark_round_evaluated, register_team_for_tournament, start_registration, start_round,
    sync_time_based_statuses,
)
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


def _submission_responses(queryset):
    # Ninja wraps schemas inside list responses a second time, which bypasses
    # their resolvers. A root model keeps the pre-resolved child schemas intact.
    return SubmissionListResponse.model_construct(root=[
        SubmissionResponse.from_orm(submission)
        for submission in queryset
    ])


def _criteria_data(criteria):
    return [
        criterion.model_dump() if hasattr(criterion, 'model_dump') else criterion
        for criterion in criteria
    ]


def _require(request, permission):
    if not has_permission(request.auth, permission):
        raise HttpError(403, 'Tournament permission required.')


def _validation_error(error):
    if hasattr(error, 'message_dict'):
        message_dict = error.message_dict
        message = next(iter(message_dict.values()), ['Invalid input data.'])[0]
    else:
        message = error.messages[0] if getattr(error, 'messages', None) else 'Invalid input data.'
    raise HttpError(400, str(message)) from None


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


def _attach_registered_team(tournament, request):
    # Whether the current user has a team registered is request-scoped (depends on
    # request.auth), so it can't be computed inside a schema resolver. We compute it
    # here and stash it on the instance; TournamentResponse.resolve_registered_team
    # just reads it back off.
    user = getattr(request, 'auth', None)
    team = None
    if user and getattr(user, 'is_authenticated', False):
        team_ids = set(user.teams.values_list('id', flat=True)) | set(
            Team.objects.filter(captain=user).values_list('id', flat=True)
        )
        registration = tournament.team_registrations.filter(
            team_id__in=team_ids, is_active=True
        ).select_related('team').first()
        team = registration.team if registration else None
    tournament._registered_team = team
    return tournament


def _team_participants(team: Team) -> list[User]:
    participants = {team.captain_id: team.captain} if team.captain_id else {}
    participants.update({member.id: member for member in team.members.all()})
    return list(participants.values())


@router.patch('/manage/{id}/banner', operation_id='updateTournamentBanner', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_tournament_banner(request, id: int, banner: UploadedFile = File(...)):
    _require(request, Permission.EDIT_TOURNAMENT)
    tournament = get_object_or_404(Tournament, pk=id)
    tournament.banner = banner
    tournament.save(update_fields=['banner'])
    return TournamentResponse.from_orm(_attach_registered_team(tournament, request))


@router.delete('/manage/{id}/banner', operation_id='deleteTournamentBanner', response={200: TournamentResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_tournament_banner(request, id: int):
    _require(request, Permission.EDIT_TOURNAMENT)
    tournament = get_object_or_404(Tournament, pk=id)
    if tournament.banner:
        tournament.banner.delete(save=False)
        tournament.banner = None
        tournament.save(update_fields=['banner'])
    return TournamentResponse.from_orm(_attach_registered_team(tournament, request))


@router.get('/{id}/registrations/{registration_pk}', operation_id='getTournamentTeamRegistration', response={200: TeamRegistrationResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_tournament_team_registration(request, id: int, registration_pk: int):
    _require(request, Permission.MANAGE_PARTICIPANTS)
    registration = get_object_or_404(
        TournamentTeamRegistration.objects.select_related('team'),
        pk=registration_pk,
        tournament_id=id,
    )
    return TeamRegistrationResponse.from_orm(registration)


@router.patch('/{id}/registrations/{registration_pk}/disqualification', operation_id='disqualifyTeamFromTournament', response={200: DisqualificationResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def disqualify_team_from_tournament(request, id: int, registration_pk: int, payload: DisqualificationRequest):
    _require(request, Permission.MANAGE_PARTICIPANTS)
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
        raise HttpError(400, 'action must be "disqualify" or "reactivate".')

    registration.save(update_fields=['is_active', 'is_disqualified', 'disqualification_reason'])
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


@router.get('/{id}/my-submissions', operation_id='listMyTeamSubmissions', response={200: SubmissionListResponse, 401: ErrorResponse, 404: ErrorResponse})
def list_my_team_submissions(request, id: int):
    tournament = get_object_or_404(Tournament, pk=id)
    registration = (
        TournamentTeamRegistration.objects.select_related('team')
        .filter(tournament=tournament, is_active=True)
        .filter(Q(team__captain_id=request.auth.id) | Q(team__team_members__user_id=request.auth.id))
        .first()
    )
    if registration is None:
        raise HttpError(404, 'No team participation found for this tournament.')
    return _submission_responses(
        _submissions().filter(round__tournament=tournament, team_id=registration.team_id)
    )


@router.get('/rounds/{id}/submissions', operation_id='listRoundSubmissions', response={200: SubmissionListResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def list_round_submissions(request, id: int):
    _require(request, Permission.SET_RESULTS)
    round_obj = get_object_or_404(Round, pk=id)
    queryset = (
        _submissions()
        .filter(round=round_obj)
        .exclude(
            team__tournament_registrations__tournament=round_obj.tournament,
            team__tournament_registrations__is_disqualified=True,
        )
    )
    return _submission_responses(queryset)


@router.get('/my-calendar', operation_id='getMyCalendar', response={200: MyCalendarResponse, 401: ErrorResponse})
def get_my_calendar(request):
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


@router.get('/{tournament_id}/certificates/delivery-status', operation_id='getTournamentCertificateDeliveryStatus', response={200: TournamentCertificateDeliveryStatusResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_tournament_certificate_delivery_status(request, tournament_id: int):
    _require(request, Permission.MANAGE_PARTICIPANTS)
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    registrations = TournamentTeamRegistration.objects.filter(
        tournament=tournament, is_active=True, is_disqualified=False
    ).select_related('team__captain').prefetch_related('team__team_members__user')
    participant_ids = set()
    for registration in registrations:
        if registration.team.captain_id:
            participant_ids.add(registration.team.captain_id)
        participant_ids.update(registration.team.team_members.values_list('user_id', flat=True))
    existing_ids = set(Certificate.objects.filter(
        tournament=tournament, user_id__in=participant_ids
    ).values_list('user_id', flat=True))
    return TournamentCertificateDeliveryStatusResponse(
        existing_count=len(existing_ids),
        missing_count=len(participant_ids - existing_ids),
    )


@router.post('/{tournament_id}/send-certificates', operation_id='sendTournamentCertificates', response={200: SendTournamentCertificatesResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def send_tournament_certificates(request, tournament_id: int, payload: SendTournamentCertificatesRequest):
    _require(request, Permission.MANAGE_PARTICIPANTS)
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    if tournament.status != Tournament.STATUS_FINISHED:
        raise HttpError(400, 'Certificates can be sent only after tournament is finished.')
    mode = payload.mode.strip().lower()
    if mode not in {'missing', 'resend'}:
        raise HttpError(400, 'mode must be "missing" or "resend".')
    template = get_object_or_404(CertificateTemplate, pk=payload.template_id)
    registrations = TournamentTeamRegistration.objects.filter(
        tournament=tournament, is_active=True, is_disqualified=False
    ).select_related('team__captain').prefetch_related('team__team_members__user')
    ranks = {row.get('team_id'): row.get('rank') for row in get_tournament_leaderboard(tournament.id, request.auth)}
    created_count = 0
    skipped_count = 0
    participant_ids = set()
    for registration in registrations:
        team = registration.team
        team_user_ids = set(team.team_members.values_list('user_id', flat=True))
        if team.captain_id:
            team_user_ids.add(team.captain_id)
        for user_id in team_user_ids - participant_ids:
            participant_ids.add(user_id)
            if mode == 'missing' and Certificate.objects.filter(tournament=tournament, user_id=user_id).exists():
                skipped_count += 1
                continue
            rank = ranks.get(team.id)
            Certificate.objects.create(
                user_id=user_id,
                team=team,
                tournament=tournament,
                placement=f'Rank #{rank}' if rank else 'Participant',
                template=template,
            )
            created_count += 1
    return SendTournamentCertificatesResponse(created_count=created_count, skipped_count=skipped_count)


@router.post('/my-calendar/export-to-google', operation_id='exportToGoogleCalendar', response={200: ExportToGoogleCalendarResponse, 400: ErrorResponse, 401: ErrorResponse})
def export_to_google_calendar(request, payload: ExportToGoogleCalendarRequest):
    if not request.auth.google_calendar_connected:
        raise HttpError(400, 'Google Calendar is not connected. Please connect first.')
    service = _get_calendar_service(request.auth)
    if not service:
        raise HttpError(400, 'Failed to connect to Google Calendar. Please reconnect.')
    if not payload.event_ids and not payload.round_ids:
        raise HttpError(400, 'Provide event_ids or round_ids to export.')

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
            errors.append({'type': 'round', 'id': round_obj.id, 'error': str(error)})
    return ExportToGoogleCalendarResponse(created=created, errors=errors)


@router.get('', auth=None, operation_id='listTournaments', response={200: TournamentListResponse, 400: ErrorResponse})
def list_tournaments(request, page: int = 1, page_size: int = 20, searchQuery: str | None = None, status: str | None = None):
    sync_time_based_statuses()
    
    if page < 1 or page_size < 1:
        raise HttpError(400, 'page and page_size must be positive integers.')
    
    queryset = _visible_tournaments(request)
    if searchQuery:
        queryset = queryset.filter(Q(name__icontains=searchQuery) | Q(description__icontains=searchQuery))
    if status:
        queryset = queryset.filter(status__in=[item.strip() for item in status.split(',') if item.strip()])
    
    total = queryset.count()
    size = min(page_size, 100)
    page_items = queryset[(page - 1) * size:page * size]
    
    # TournamentResponse.from_orm runs Ninja's field resolvers. Constructing the
    # enclosing schema normally re-wraps each child in DjangoGetter and loses them.
    return TournamentListResponse.model_construct(
        data=[
            TournamentResponse.from_orm(
                _attach_registered_team(tournament, request),
            )
            for tournament in page_items
        ],
        total=total,
    )


@router.get('/archive', operation_id='listTournamentArchive', response={200: list[TournamentArchiveListResponse], 401: ErrorResponse})
def list_tournament_archive(request):
    queryset = Tournament.objects.filter(status=Tournament.STATUS_FINISHED).prefetch_related('rounds')
    
    return [TournamentArchiveListResponse.model_validate(tournament, from_attributes=True) for tournament in queryset]


@router.get('/archive/{id}', operation_id='getTournamentArchive', response={200: TournamentArchiveDetailResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_tournament_archive(request, id: int):
    tournament = get_object_or_404(Tournament.objects.prefetch_related('rounds'), pk=id, status=Tournament.STATUS_FINISHED)
    
    return TournamentArchiveDetailResponse.model_validate(tournament, from_attributes=True)


@router.get('/archive/{id}/submissions', operation_id='listTournamentArchiveSubmissions', response={200: SubmissionListResponse, 401: ErrorResponse, 404: ErrorResponse})
def list_tournament_archive_submissions(request, id: int):
    get_object_or_404(Tournament, pk=id, status=Tournament.STATUS_FINISHED)
    queryset = _submissions().filter(round__tournament_id=id)

    return _submission_responses(queryset)


@router.get('/{int:id}', auth=None, operation_id='getTournament', response={200: TournamentResponse, 404: ErrorResponse})
def get_tournament(request, id: int):
    tournament = get_object_or_404(_visible_tournaments(request), pk=id)

    return TournamentResponse.model_validate(_attach_registered_team(tournament, request), from_attributes=True)


@router.post('/manage', operation_id='createTournament', response={201: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_tournament(request, payload: TournamentCreateRequest):
    _require(request, Permission.CREATE_TOURNAMENT)
    tournament = _validate_model(Tournament(created_by=request.auth, **payload.model_dump()))
    tournament.save()
    
    tournament = _attach_registered_team(tournament, request)

    return 201, TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
    )


@router.get('/manage/{id}', operation_id='getTournamentForUpdate', response={200: TournamentResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_tournament_for_update(request, id: int):
    _require(request, Permission.VIEW_TOURNAMENT)
    tournament = get_object_or_404(Tournament, pk=id)
    
    return TournamentResponse.model_validate(_attach_registered_team(tournament, request), from_attributes=True)


def _save_tournament(request, pk, payload):
    _require(request, Permission.EDIT_TOURNAMENT)

    tournament = _update_model(get_object_or_404(Tournament, pk=pk), payload.model_dump(exclude_unset=True))
    tournament.save()

    return tournament


@router.put('/manage/{id}', operation_id='replaceTournament', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def replace_tournament(request, id: int, payload: TournamentCreateRequest):
    tournament = _attach_registered_team(
        _save_tournament(request, id, payload),
        request,
    )

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
    )


@router.patch('/manage/{id}', operation_id='updateTournament', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_tournament(request, id: int, payload: TournamentUpdateRequest):
    tournament = _attach_registered_team(
        _save_tournament(request, id, payload),
        request,
    )

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
    )


@router.delete('/manage/{id}', operation_id='deleteTournament', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_tournament(request, id: int):
    _require(request, Permission.DELETE_TOURNAMENT)
    get_object_or_404(Tournament, pk=id).delete()
    
    return 204, None


@router.post('/{id}/start-registration', operation_id='startTournamentRegistration', response={200: TournamentResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def start_tournament_registration(request, id: int):
    _require(request, Permission.EDIT_TOURNAMENT)
    
    try:
        tournament = start_registration(get_object_or_404(Tournament, pk=id))
    except ValidationError as error:
        _validation_error(error)
    
    tournament = _attach_registered_team(tournament, request)

    return TournamentResponse.model_validate(
        tournament,
        from_attributes=True,
    )


@router.post('/{id}/register-team', operation_id='registerTeamForTournament', response={201: TeamRegistrationResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def register_team(request, id: int, payload: TeamRegistrationRequest):
    tournament = get_object_or_404(Tournament, pk=id)
    team = get_object_or_404(Team, pk=payload.team_id)
    
    try:
        registration = register_team_for_tournament(tournament=tournament, team=team, actor=request.auth)
    except ValidationError as error:
        _validation_error(error)
    
    NotificationService.notify(recipients=_participants(tournament), event_type='tournament_team_registered', context={'team_name': team.name, 'tournament_name': tournament.name})
    return 201, TeamRegistrationResponse.model_validate(registration, from_attributes=True)


@router.post('/{id}/leave-team', operation_id='unregisterTeamFromTournament', response={200: TeamRegistrationResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def leave_team(request, id: int, payload: TeamRegistrationRequest):
    tournament = get_object_or_404(Tournament, pk=id)
    team = get_object_or_404(Team, pk=payload.team_id)
    
    try:
        registration = leave_team_from_tournament(tournament=tournament, team=team, actor=request.auth)
    except ValidationError as error:
        _validation_error(error)
    
    return TeamRegistrationResponse.model_validate(registration, from_attributes=True)


@router.get('/{id}/eligible-teams', operation_id='listEligibleTeamsForTournament', response={200: list[EligibleTeamResponse], 401: ErrorResponse, 404: ErrorResponse})
def list_eligible_teams(request, id: int):
    get_object_or_404(Tournament, pk=id)
    queryset = Team.objects.filter(captain_id=request.auth.id).annotate(members_count=Count('team_members', distinct=True))
    
    return [EligibleTeamResponse.model_validate(team, from_attributes=True) for team in queryset]


@router.get('/{id}/teams', operation_id='listTournamentTeams', response={200: list[TournamentTeamResponse], 401: ErrorResponse, 404: ErrorResponse})
def list_tournament_teams(request, id: int, status: str = 'active'):
    get_object_or_404(Tournament, pk=id)
    queryset = TournamentTeamRegistration.objects.filter(tournament_id=id).select_related('team', 'team__captain').prefetch_related('team__members')
    
    if status == 'disqualified':
        queryset = queryset.filter(is_disqualified=True)
    elif status != 'all':
        queryset = queryset.filter(is_active=True)
    
    return queryset


@router.get('/active', operation_id='getTeamActiveTournament', response={200: ActiveTournamentResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_active_tournament(request, team_id: int):
    registration = TournamentTeamRegistration.objects.select_related('tournament').filter(team_id=team_id, is_active=True, tournament__status__in=[Tournament.STATUS_REGISTRATION, Tournament.STATUS_RUNNING]).first()
    
    if registration is None:
        raise HttpError(404, 'Active tournament not found for this team.')
    
    return ActiveTournamentResponse.model_validate(registration.tournament, from_attributes=True)


@router.get('/{tournament_pk}/rounds', operation_id='listRounds', response={200: list[RoundResponse], 401: ErrorResponse, 404: ErrorResponse})
def list_rounds(request, tournament_pk: int, status: str | None = None):
    tournament = get_object_or_404(Tournament, pk=tournament_pk)
    queryset = _rounds().filter(tournament=tournament)
    
    if not has_permission(request.auth, Permission.VIEW_TOURNAMENT):
        queryset = queryset.exclude(status=Round.STATUS_DRAFT)
    if status:
        queryset = queryset.filter(status__in=[item.strip() for item in status.split(',') if item.strip()])
    
    return queryset


@router.post('/{tournament_pk}/rounds', operation_id='createRound', response={201: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def create_round(request, tournament_pk: int, payload: RoundCreateRequest):
    _require(request, Permission.MANAGE_ROUNDS)
    
    tournament = get_object_or_404(Tournament, pk=tournament_pk)
    data = payload.model_dump()
    data['criteria'] = _criteria_data(data['criteria'])
    
    round_obj = _validate_model(Round(tournament=tournament, **data))
    round_obj.save()
    
    return 201, round_obj


@router.get('/rounds/{id}', operation_id='getRound', response={200: RoundResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_round(request, id: int):
    round_obj = get_object_or_404(_rounds(), pk=id)
    
    return round_obj


def _save_round(request, pk, payload):
    _require(request, Permission.MANAGE_ROUNDS)
    values = payload.model_dump(exclude_unset=True)
    
    if 'criteria' in values and values['criteria'] is not None:
        values['criteria'] = _criteria_data(values['criteria'])
    
    round_obj = _update_model(get_object_or_404(_rounds(), pk=pk), values)
    round_obj.save()
    
    return round_obj


@router.put('/rounds/{id}', operation_id='replaceRound', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def replace_round(request, id: int, payload: RoundCreateRequest):
    return _save_round(request, id, payload)


@router.patch('/rounds/{id}', operation_id='updateRound', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_round(request, id: int, payload: RoundUpdateRequest):
    return _save_round(request, id, payload)


@router.delete('/rounds/{id}', operation_id='deleteRound', response={204: None, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_round_view(request, id: int):
    _require(request, Permission.MANAGE_ROUNDS)
    
    try:
        delete_round(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    
    return 204, None


@router.post('/rounds/{id}/start', operation_id='startRound', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def start_round_view(request, id: int):
    _require(request, Permission.MANAGE_ROUNDS)
    
    try:
        round_obj = start_round(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    
    return round_obj


@router.post('/rounds/{id}/close-submissions', operation_id='closeRoundSubmissions', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def close_round_submissions(request, id: int):
    _require(request, Permission.MANAGE_ROUNDS)
    
    try:
        round_obj = close_submissions_on_round(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    
    return round_obj


@router.post('/rounds/{id}/mark-evaluated', operation_id='markRoundEvaluated', response={200: RoundResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def mark_round_evaluated_view(request, id: int):
    _require(request, Permission.SET_RESULTS)
    
    try:
        round_obj = mark_round_evaluated(get_object_or_404(_rounds(), pk=id))
    except ValidationError as error:
        _validation_error(error)
    
    return round_obj


@router.get('/submissions', operation_id='listSubmissions', response={200: list[OwnSubmissionResponse], 401: ErrorResponse})
def list_submissions(request):
    queryset = _submissions().filter(
        Q(team__captain_id=request.auth.id) | Q(team__team_members__user_id=request.auth.id)
    ).distinct()
    
    return queryset


@router.post('/submissions', operation_id='createSubmission', response={201: SubmissionResponse, 400: ErrorResponse, 401: ErrorResponse})
def create_submission(request, payload: SubmissionCreateRequest):
    round_obj = get_object_or_404(Round.objects.select_related('tournament'), pk=payload.round)
    team = Team.objects.filter(captain=request.auth).filter(tournament_registrations__tournament=round_obj.tournament, tournament_registrations__is_active=True).first()
    
    if team is None:
        raise HttpError(400, 'Only team captain can create submissions for an active registered team in this tournament.')
    submission = Submission(team=team, round=round_obj, created_by=request.auth, **payload.model_dump(exclude={'round'}))
    
    _validate_model(submission)
    
    try:
        submission.save()
    except IntegrityError:
        raise HttpError(400, 'Only one submission per team per round is allowed.') from None
    
    return 201, _submissions().get(pk=submission.pk)


@router.get('/submissions/{id}', operation_id='getSubmission', response={200: SubmissionResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_submission(request, id: int):
    submission = get_object_or_404(_submissions().filter(team__captain_id=request.auth.id), pk=id)
    
    return submission


def _save_submission(request, pk, payload):
    submission = get_object_or_404(_submissions().filter(team__captain_id=request.auth.id), pk=pk)
    
    _update_model(submission, payload.model_dump(exclude_unset=True))
    submission.save()
    
    return _submissions().get(pk=submission.pk)


@router.put('/submissions/{id}', operation_id='replaceSubmission', response={200: SubmissionResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def replace_submission(request, id: int, payload: SubmissionCreateRequest):
    return _save_submission(request, id, SubmissionUpdateRequest(**payload.model_dump(exclude={'round'})))


@router.patch('/submissions/{id}', operation_id='updateSubmission', response={200: SubmissionResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse})
def update_submission(request, id: int, payload: SubmissionUpdateRequest):
    return _save_submission(request, id, payload)


@router.get('/{id}/submissions', operation_id='listTournamentSubmissions', response={200: SubmissionListResponse, 401: ErrorResponse})
def list_tournament_submissions(request, id: int):
    queryset = _submissions().filter(round__tournament_id=id)
    return _submission_responses(queryset)


@router.get('/current-task', operation_id='getCurrentTask', response={200: CurrentTaskResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_current_task(request, tournament_id: int | None = None):
    queryset = Round.objects.filter(
        status=Round.STATUS_ACTIVE,
        tournament__status=Tournament.STATUS_RUNNING,
    ).select_related('tournament').order_by('end_date', 'id')
    if tournament_id is not None:
        queryset = queryset.filter(tournament_id=tournament_id)

    round_obj = queryset.first()
    if round_obj is None:
        raise HttpError(404, 'No active task found.')
    return CurrentTaskResponse.model_validate(round_obj, from_attributes=True)


@router.get('/icons', operation_id='listIcons', response={200: list[IconResponse], 401: ErrorResponse})
def list_icons(request):
    return [IconResponse.model_validate(icon, from_attributes=True) for icon in Icon.objects.all()]


def _save_event(request, payload, instance=None):
    _require(request, Permission.MANAGE_ROUNDS)
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
    return event


@router.get('/events', operation_id='listEvents', response={200: EventListResponse, 401: ErrorResponse})
def list_events(request, tournament: int | None = None):
    events = Event.objects.all()
    if tournament is not None:
        events = events.filter(tournament_id=tournament)

    return EventListResponse.model_construct(root=[
        EventResponse.model_validate(event, from_attributes=True)
        for event in events
    ])


@router.post('/events', operation_id='createEvent', response={201: EventResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse})
def create_event(request, payload: EventCreateRequest):
    return 201, EventResponse.model_validate(_save_event(request, payload), from_attributes=True)


@router.get('/events/{id}', operation_id='getEvent', response={200: EventResponse, 401: ErrorResponse, 404: ErrorResponse})
def get_event(request, id: int):
    event = get_object_or_404(Event, pk=id)
    return EventResponse.model_validate(event, from_attributes=True)


@router.patch('/events/{id}', operation_id='updateEvent', response={200: EventResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def update_event(request, id: int, payload: EventUpdateRequest):
    return EventResponse.model_validate(_save_event(request, payload, get_object_or_404(Event, pk=id)), from_attributes=True)


@router.delete('/events/{id}', operation_id='deleteEvent', response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def delete_event(request, id: int):
    _require(request, Permission.MANAGE_ROUNDS)
    get_object_or_404(Event, pk=id).delete()
    
    return 204, None
