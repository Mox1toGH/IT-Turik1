from datetime import datetime

from ninja import Schema
from pydantic import JsonValue, RootModel

from backend.media import absolute_media_url
from backend.schemas import CalendarEventType, RoundStatus, TournamentStatus, UserRole


def _file_url(file_field, context=None):
    return absolute_media_url(file_field, context)


def _parse_criteria(raw):
    return [
        {
            'id': item.get('id', ''),
            'name': item.get('name', ''),
            'description': item.get('description', ''),
            'max_score': item.get('max_score', 0),
        }
        for item in raw
    ]


def _team_members(team):
    members = list(team.members.all())
    if team.captain_id not in {member.id for member in members}:
        members.append(team.captain)
    return members


class CriterionResponse(Schema):
    id: str
    name: str
    description: str
    max_score: float


class TeamSummaryResponse(Schema):
    id: int
    name: str
    is_public: bool


class TeamMemberResponse(Schema):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    avatar: str | None = None
    avatar_frame_url: str | None = None

    @staticmethod
    def resolve_avatar(obj, context):
        return _file_url(obj.avatar, context)


class RoundShortResponse(Schema):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    status: RoundStatus
    criteria: list[CriterionResponse]
    tournament: int

    @staticmethod
    def resolve_criteria(obj):
        return _parse_criteria(obj.criteria)

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id


class TournamentResponse(Schema):
    id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    max_teams: int | None = None
    min_team_members: int | None = None
    banner: str | None = None
    status: TournamentStatus
    rounds: list[RoundShortResponse]
    registered_team: TeamSummaryResponse | None = None

    @staticmethod
    def resolve_banner(obj, context):
        return _file_url(obj.banner, context)

    @staticmethod
    def resolve_rounds(obj):
        return obj.rounds.all()

    @staticmethod
    def resolve_registered_team(obj):
        # Populated by views._attach_registered_team before the object is returned,
        # since resolvers don't have access to the request/current user.
        return getattr(obj, '_registered_team', None)


class TournamentListResponse(Schema):
    data: list[TournamentResponse]
    total: int


class ActiveTournamentResponse(Schema):
    id: int
    name: str
    status: TournamentStatus
    start_date: datetime


class RoundBreakdownResponse(Schema):
    round_id: int
    round_name: str
    total_score: float
    average_score: float
    criteria_breakdown: dict[str, float]
    jury_breakdown: dict[str, float] | None = None


class ArchiveStandingResponse(Schema):
    rank: int
    team: TeamSummaryResponse
    total_score: float
    average_score: float
    criteria_breakdown: dict[str, float]
    jury_breakdown: dict[str, float] | None = None
    rounds_breakdown: list[RoundBreakdownResponse] | None = None
    snapshot_at: datetime


class TournamentArchiveListResponse(Schema):
    id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: TournamentStatus
    banner: str | None = None
    teams: list[TeamSummaryResponse]
    standings: list[ArchiveStandingResponse]

    @staticmethod
    def resolve_banner(obj, context):
        return _file_url(obj.banner, context)

    @staticmethod
    def resolve_teams(obj):
        return [
            registration.team
            for registration in obj.team_registrations.filter(is_active=True)
            .select_related('team')
            .order_by('team__name')
        ]

    @staticmethod
    def resolve_standings(obj):
        return obj.leaderboard_entries.filter(round__isnull=True).select_related('team').order_by('rank')


class TournamentArchiveDetailResponse(TournamentArchiveListResponse):
    rounds: list[RoundShortResponse]

    @staticmethod
    def resolve_rounds(obj):
        return obj.rounds.all()


class TournamentCreateRequest(Schema):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    max_teams: int | None = None
    min_team_members: int | None = None


class TournamentUpdateRequest(Schema):
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    max_teams: int | None = None
    min_team_members: int | None = None


class RoundResponse(Schema):
    id: int
    tournament: int
    name: str
    description: dict[str, JsonValue]
    tech_requirements: dict[str, JsonValue]
    must_have_requirements: dict[str, JsonValue]
    criteria: list[CriterionResponse]
    start_date: datetime
    end_date: datetime
    passing_count: int | None = None
    evaluation_criteria: str
    materials: list[JsonValue]
    status: RoundStatus

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id

    @staticmethod
    def resolve_criteria(obj):
        return _parse_criteria(obj.criteria)


class RoundCreateRequest(Schema):
    name: str = ''
    description: dict[str, JsonValue] = {}
    tech_requirements: dict[str, JsonValue] = {}
    must_have_requirements: dict[str, JsonValue] = {}
    criteria: list[CriterionResponse] = []
    start_date: datetime
    end_date: datetime
    passing_count: int | None = None
    evaluation_criteria: str = 'score'
    materials: list[JsonValue] = []


class RoundUpdateRequest(Schema):
    name: str | None = None
    description: dict[str, JsonValue] | None = None
    tech_requirements: dict[str, JsonValue] | None = None
    must_have_requirements: dict[str, JsonValue] | None = None
    criteria: list[CriterionResponse] | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    passing_count: int | None = None
    evaluation_criteria: str | None = None
    materials: list[JsonValue] | None = None


class TeamRegistrationRequest(Schema):
    team_id: int


class TeamRegistrationResponse(Schema):
    id: int
    tournament: int
    team: int
    team_name: str
    is_active: bool
    is_disqualified: bool
    disqualification_reason: str | None = None
    created_at: datetime

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id

    @staticmethod
    def resolve_team(obj):
        return obj.team_id

    @staticmethod
    def resolve_team_name(obj):
        return obj.team.name


class EligibleTeamResponse(Schema):
    id: int
    name: str
    members_count: int


class TournamentTeamResponse(Schema):
    id: int
    registration_id: int
    name: str
    members_count: int
    members: list[TeamMemberResponse]
    is_public: bool
    is_active: bool
    is_disqualified: bool
    disqualification_reason: str | None = None

    @staticmethod
    def resolve_id(obj):
        return obj.team_id

    @staticmethod
    def resolve_registration_id(obj):
        return obj.id

    @staticmethod
    def resolve_name(obj):
        return obj.team.name

    @staticmethod
    def resolve_is_public(obj):
        return obj.team.is_public

    @staticmethod
    def resolve_members(obj):
        return _team_members(obj.team)

    @staticmethod
    def resolve_members_count(obj):
        return len(_team_members(obj.team))


class JuryResponse(Schema):
    id: int
    username: str
    full_name: str
    role: UserRole


class ScoreResponse(Schema):
    criterion_id: str
    criterion_name: str
    score: int


class SubmissionEvaluationResponse(Schema):
    id: int
    scores: list[ScoreResponse]
    total_score: float
    final_score: float
    comment: str
    created_at: datetime


class SubmissionAssignmentResponse(Schema):
    id: int
    jury: JuryResponse
    evaluation: SubmissionEvaluationResponse | None = None
    created_at: datetime

    @staticmethod
    def resolve_evaluation(obj):
        # Reverse one-to-one descriptors raise DoesNotExist (which subclasses
        # AttributeError), so getattr(..., default) safely yields None.
        return getattr(obj, 'evaluation', None)


class SubmissionResponse(Schema):
    id: int
    team: int
    round: int
    team_details: TeamSummaryResponse
    round_details: RoundShortResponse
    github_url: str
    demo_video_url: str
    demo_video_file: str | None = None
    live_demo_url: str
    description: str
    assignments: list[SubmissionAssignmentResponse]
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_team(obj):
        return obj.team_id

    @staticmethod
    def resolve_round(obj):
        return obj.round_id

    @staticmethod
    def resolve_team_details(obj):
        return obj.team

    @staticmethod
    def resolve_round_details(obj):
        return obj.round

    @staticmethod
    def resolve_demo_video_file(obj, context):
        return _file_url(obj.demo_video_file, context)

    @staticmethod
    def resolve_assignments(obj):
        return obj.jury_assignments.all()


class SubmissionListResponse(RootModel[list[SubmissionResponse]]):
    pass


class OwnSubmissionResponse(Schema):
    id: int
    team: TeamSummaryResponse
    round: RoundShortResponse
    github_url: str
    demo_video_url: str
    demo_video_file: str | None = None
    live_demo_url: str
    description: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_demo_video_file(obj, context):
        return _file_url(obj.demo_video_file, context)


class SubmissionCreateRequest(Schema):
    round: int
    github_url: str
    demo_video_url: str = ''
    live_demo_url: str = ''
    description: str = ''


class SubmissionUpdateRequest(Schema):
    github_url: str | None = None
    demo_video_url: str | None = None
    live_demo_url: str | None = None
    description: str | None = None


class CurrentTaskResponse(Schema):
    id: int
    tournament_id: int
    tournament_name: str
    name: str
    task: dict[str, JsonValue]
    deadline: datetime
    must_have_requirements: dict[str, JsonValue]
    tech_requirements: dict[str, JsonValue]

    @staticmethod
    def resolve_tournament_name(obj):
        return obj.tournament.name

    @staticmethod
    def resolve_task(obj):
        return obj.description

    @staticmethod
    def resolve_deadline(obj):
        return obj.end_date


class IconResponse(Schema):
    id: int
    name: str
    path: str


class EventResponse(Schema):
    id: int
    tournament: int
    type: CalendarEventType
    title: str
    description: str
    link: str
    start_datetime: datetime
    icon: int | None = None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id

    @staticmethod
    def resolve_icon(obj):
        return obj.icon_id


class EventListResponse(RootModel[list[EventResponse]]):
    pass


class EventCreateRequest(Schema):
    tournament: int
    type: CalendarEventType
    title: str
    description: str = ''
    link: str = ''
    start_datetime: datetime
    icon: int | None = None


class EventUpdateRequest(Schema):
    tournament: int | None = None
    type: CalendarEventType | None = None
    title: str | None = None
    description: str | None = None
    link: str | None = None
    start_datetime: datetime | None = None
    icon: int | None = None


class DisqualificationRequest(Schema):
    action: str
    disqualification_reason: str = ''


class DisqualificationResponse(Schema):
    id: int
    team_id: int
    team_name: str
    tournament_id: int
    is_active: bool
    action: str


class CalendarEventResponse(Schema):
    id: int
    tournament: int
    type: CalendarEventType
    title: str
    description: str
    link: str
    start_datetime: datetime
    icon: int | None = None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id

    @staticmethod
    def resolve_icon(obj):
        return obj.icon_id


class CalendarRoundResponse(Schema):
    id: int
    tournament: int
    name: str
    description: dict[str, JsonValue]
    tech_requirements: dict[str, JsonValue]
    must_have_requirements: dict[str, JsonValue]
    criteria: list[CriterionResponse]
    start_date: datetime
    end_date: datetime
    passing_count: int | None = None
    evaluation_criteria: str
    materials: list[JsonValue]
    status: RoundStatus

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id

    @staticmethod
    def resolve_criteria(obj):
        return _parse_criteria(obj.criteria)


class MyCalendarResponse(Schema):
    events: list[CalendarEventResponse]
    rounds: list[CalendarRoundResponse]


class TournamentCertificateDeliveryStatusResponse(Schema):
    existing_count: int
    missing_count: int


class SendTournamentCertificatesRequest(Schema):
    template_id: int
    mode: str = 'missing'


class SendTournamentCertificatesResponse(Schema):
    created_count: int
    skipped_count: int


class ExportToGoogleCalendarRequest(Schema):
    event_ids: list[int] = []
    round_ids: list[int] = []


class ExportedCalendarItemResponse(Schema):
    type: str
    id: int
    google_event_id: str | None = None
    google_event_ids: list[str] | None = None
    html_link: str | None = None


class CalendarExportErrorResponse(Schema):
    type: str
    id: int
    error: str


class ExportToGoogleCalendarResponse(Schema):
    created: list[ExportedCalendarItemResponse]
    errors: list[CalendarExportErrorResponse]
