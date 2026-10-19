from datetime import datetime

from ninja import Schema
from pydantic import JsonValue

from backend.schemas import CalendarEventType, RoundStatus, TournamentStatus, UserRole

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

class RoundShortResponse(Schema):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    status: RoundStatus
    criteria: list[CriterionResponse]
    tournament: int

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
    standings: list[ArchiveStandingResponse]

class TournamentArchiveDetailResponse(Schema):
    id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: TournamentStatus
    banner: str | None = None
    teams: list[TeamSummaryResponse]
    standings: list[ArchiveStandingResponse]
    rounds: list[RoundShortResponse]

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

class EligibleTeamResponse(Schema):
    id: int
    name: str
    members_count: int
    reason: str | None = None

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

class MyCalendarResponse(Schema):
    events: list[CalendarEventResponse]
    rounds: list[CalendarRoundResponse]

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
