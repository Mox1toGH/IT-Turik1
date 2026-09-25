from datetime import datetime
from typing import Annotated, Any, Literal, Optional

from ninja import Field, Schema
from pydantic import field_validator
from tournaments.schemas import CriterionResponse

# Adjust these two imports to whatever your tournaments/schemas.py exports
# (replacements for SubmissionSerializer / CriterionSerializer).

# =============================================================================
# Requests
# =============================================================================

class JuryAssignmentFilters(Schema):
    """Query params for GET /jury-assignments (page / page_size come from the paginator)."""
    round_id: int | None = Field(None, description='Filter by single round ID')
    round_ids: str | None = Field(None, description='Comma-separated round IDs')
    tournament_ids: str | None = Field(None, description='Comma-separated tournament IDs')
    evaluation_status: Literal['all', 'evaluated', 'not_evaluated'] = Field(
        'all', description='all | evaluated | not_evaluated'
    )


class ScoreItemRequest(Schema):
    # criterion_name is derived from the round's criteria on the server,
    # so it is not part of the request (extra keys sent by old clients are ignored).
    criterion_id: str
    score: int


class SubmissionEvaluationRequest(Schema):
    """POST (create) and PUT (full replace)."""
    tournament_id: int
    assignment: int
    scores: list[ScoreItemRequest]
    comment: str = ''


class SubmissionEvaluationPatchRequest(Schema):
    """PATCH - every field optional."""
    tournament_id: int | None = None
    assignment: int | None = None
    scores: list[ScoreItemRequest] | None = None
    comment: str | None = None


class JuryAssignmentItemRequest(Schema):
    submission: int
    jury: Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]

    @field_validator('jury')
    @classmethod
    def no_duplicate_jury(cls, value):
        if len(value) != len(set(value)):
            raise ValueError('Duplicate jury user ids are not allowed for a submission.')
        return value


# =============================================================================
# Evaluations / assignments
# =============================================================================

class ScoreItemResponse(Schema):
    criterion_id: str
    criterion_name: str | None = None
    score: int


class SubmissionEvaluationResponse(Schema):
    id: int
    assignment: int
    scores: list[ScoreItemResponse]
    total_score: float | None = None
    final_score: float | None = None
    comment: str | None = None
    created_at: datetime

    @staticmethod
    def resolve_assignment(obj):
        return obj.assignment_id


class RoundShortResponse(Schema):
    id: int
    name: str
    start_date: datetime | None = None  # use `date` if these are DateFields
    end_date: datetime | None = None
    status: str
    criteria: list[CriterionResponse]
    tournament: int

    @staticmethod
    def resolve_tournament(obj):
        return obj.tournament_id


class JuryAssignmentResponse(Schema):
    id: int
    submission: int
    submission_details: Any # SubmissionResponse
    round_details: RoundShortResponse
    evaluation: SubmissionEvaluationResponse | None = None
    is_evaluated: bool
    created_at: datetime

    @staticmethod
    def resolve_submission(obj):
        return obj.submission_id

    @staticmethod
    def resolve_submission_details(obj):
        return obj.submission

    @staticmethod
    def resolve_round_details(obj):
        return obj.submission.round

    @staticmethod
    def resolve_evaluation(obj):
        # reverse one-to-one: raises if missing, getattr default swallows it
        return getattr(obj, 'evaluation', None)

    @staticmethod
    def resolve_is_evaluated(obj):
        return hasattr(obj, 'evaluation')


class AvailableJuryResponse(Schema):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None


class AssignJuryResponse(Schema):
    status: str
    created_assignments: int


# =============================================================================
# Leaderboards
# =============================================================================

class RankingItemResponse(Schema):
    team_id: int
    team_name: str
    total_score: float
    average_score: float
    rank: int


class RoundLeaderboardResponse(Schema):
    round_id: int
    is_snapshot: bool
    rankings: list[RankingItemResponse]


class RoundSummaryResponse(Schema):
    round_id: int
    round_name: str
    total_score: float
    average_score: float
    jury_breakdown: Any | None = None


class TournamentRankingItemResponse(Schema):
    team_id: int
    team_name: str
    total_score: float
    rank: int
    rounds: list[RoundSummaryResponse]


class TournamentLeaderboardResponse(Schema):
    tournament_id: int
    is_snapshot: bool
    rankings: list[TournamentRankingItemResponse]


# =============================================================================
# Passing status
# =============================================================================

class PassingStatusItemResponse(Schema):
    rank: int
    team_id: int
    team_name: str
    total_score: float
    average_score: float
    passed: bool
    is_active: bool | None = None
    disqualification_reason: str | None = None
    registration_id: int | None = None


class RoundPassingStatusResponse(Schema):
    round_id: int
    round_name: str
    passing_count: int | None = None
    total_teams: int
    results: list[PassingStatusItemResponse]
