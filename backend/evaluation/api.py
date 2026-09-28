from typing import Any

from django.shortcuts import get_object_or_404

from ninja import Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PaginationBase, paginate

from backend.auth import JWTAuth

from tournaments.models import Round, Submission, Tournament, TournamentTeamRegistration

from .leaderboard_service import compute_leaderboard, get_leaderboard, get_tournament_leaderboard
from .models import JuryAssignment, SubmissionEvaluation
from .realtime import emit_tournament_leaderboard_updated

from backend.schemas import ErrorResponse
from backend.permissions import Permission, has_permission
from .schemas import (
    AssignJuryResponse,
    AvailableJuryResponse,
    JuryAssignmentFilters,
    JuryAssignmentItemRequest,
    JuryAssignmentResponse,
    RoundLeaderboardResponse,
    RoundPassingStatusResponse,
    SubmissionEvaluationPatchRequest,
    SubmissionEvaluationRequest,
    SubmissionEvaluationResponse,
    TournamentLeaderboardResponse,
)
from .services import get_available_jury, replace_round_jury_assignments, try_auto_evaluate_round

router = Router(tags=['evaluation'], auth=JWTAuth())

def _require_evaluation_access(request):
    if not has_permission(request.auth, Permission.MANAGE_EVALUATIONS):
        raise HttpError(403, 'You do not have permission to manage evaluations.')


def _require_assignment_management(request):
    if not has_permission(request.auth, Permission.MANAGE_ASSIGNMENTS):
        raise HttpError(403, 'You do not have permission to manage assignments.')


class JuryAssignmentPagination(PaginationBase):
    class Input(Schema):
        page: int = 1
        page_size: int = 8

    class Output(Schema):
        items: list[Any]
        count: int
        evaluated_count: int

    def paginate_queryset(self, queryset, pagination: Input, **params):
        page = max(pagination.page, 1)
        page_size = min(max(pagination.page_size, 1), 100)
        offset = (page - 1) * page_size
        return {
            'items': queryset[offset:offset + page_size],
            'count': self._items_count(queryset),
            'evaluated_count': queryset.filter(evaluation__isnull=False).count(),
        }


# =============================================================================
# Jury assignments (juror's own)
#
#   GET /jury-assignments                     -> list_jury_assignments
#   GET /jury-assignments/{assignment_id}     -> get_jury_assignment
# =============================================================================

def _own_assignments(user):
    return JuryAssignment.objects.filter(jury=user).select_related(
        'submission',
        'submission__team',
        'submission__round',
        'submission__round__tournament',
        'evaluation',
    )


def _parse_ids_list(value: str | None, field_name: str) -> list[int]:
    if not value:
        return []

    try:
        ids = [int(item.strip()) for item in value.split(',') if item.strip()]
    except ValueError:
        raise HttpError(400, f'{field_name}: IDs must be positive numbers.')

    if any(id <= 0 for id in ids):
        raise HttpError(400, f'{field_name}: IDs must be positive numbers.')

    return ids


@router.get(
    '/jury-assignments',
    operation_id='listJuryAssignments',
    url_name="jury-assignments",
    response={200: list[JuryAssignmentResponse], 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse},
)
@paginate(JuryAssignmentPagination)
def list_jury_assignments(request, filters: JuryAssignmentFilters = Query(...)):
    _require_assignment_management(request)

    qs = _own_assignments(request.auth).order_by('-created_at', '-id')

    if filters.round_id:
        qs = qs.filter(submission__round_id=filters.round_id)

    round_ids = _parse_ids_list(filters.round_ids, 'round_ids')
    if round_ids:
        qs = qs.filter(submission__round_id__in=round_ids)

    tournament_ids = _parse_ids_list(filters.tournament_ids, 'tournament_ids')
    if tournament_ids:
        qs = qs.filter(submission__round__tournament_id__in=tournament_ids)

    if filters.evaluation_status == 'evaluated':
        qs = qs.filter(evaluation__isnull=False)
    elif filters.evaluation_status == 'not_evaluated':
        qs = qs.filter(evaluation__isnull=True)

    return qs


# =============================================================================
# Jury evaluations
#
#   POST   /jury-evaluations                    -> create_jury_evaluation
#   GET    /jury-evaluations/{evaluation_id}    -> get_jury_evaluation
#   PUT    /jury-evaluations/{evaluation_id}    -> replace_jury_evaluation
#   PATCH  /jury-evaluations/{evaluation_id}    -> update_jury_evaluation
#   DELETE /jury-evaluations/{evaluation_id}    -> delete_jury_evaluation
# =============================================================================

def _own_evaluations(user):
    return SubmissionEvaluation.objects.select_related(
        'assignment', 'assignment__submission', 'assignment__submission__round',
    ).filter(assignment__jury=user)


def _get_assignment(user, assignment_id: int):
    assignment = (
        JuryAssignment.objects
        .select_related('submission', 'submission__round')
        .filter(pk=assignment_id)
        .first()
    )

    if assignment is None:
        raise HttpError(400, 'Assignment not found.')

    if assignment.jury_id != user.id:
        raise HttpError(400, 'You are not assigned to this submission.')

    return assignment


def _check_tournament(assignment, tournament_id: int | None):
    if tournament_id is not None and assignment.submission.round.tournament_id != tournament_id:
        raise HttpError(400, 'tournament_id: Assignment does not belong to this tournament.')


def _build_scores(round_obj, scores: list[dict]) -> list[dict]:
    """Validate scores against the round's criteria and enrich them with criterion names."""
    criteria = round_obj.criteria
    if not criteria:
        raise HttpError(400, 'scores: Round has no evaluation criteria.')

    criteria_by_id = {c['id']: c for c in criteria}
    seen: set[str] = set()
    enriched = []

    for item in scores:
        c_id = item['criterion_id']
        criterion = criteria_by_id.get(c_id)
        if criterion is None:
            raise HttpError(400, f'scores: Invalid criterion_id: {c_id}')
        if c_id in seen:
            raise HttpError(400, f'scores: Duplicate criterion_id: {c_id}')

        score = item['score']
        max_score = criterion['max_score']
        if score < 0 or score > max_score:
            raise HttpError(400, f'scores: Invalid score for {c_id}. Must be between 0 and {max_score}')

        seen.add(c_id)
        enriched.append({
            'criterion_id': c_id,
            'criterion_name': criterion.get('name'),
            'score': score,
        })

    missing = set(criteria_by_id) - seen
    if missing:
        raise HttpError(400, f'scores: Missing scores for criteria: {", ".join(sorted(missing))}')

    return enriched


def _after_evaluation_saved(evaluation, reason: str):
    submission = evaluation.assignment.submission
    round_obj = submission.round
    try_auto_evaluate_round(round_obj)
    emit_tournament_leaderboard_updated(
        tournament_id=round_obj.tournament_id,
        round_id=round_obj.id,
        reason=reason,
        submission_id=submission.id,
        evaluation_id=evaluation.id,
    )


@router.post(
    '/jury-evaluations',
    operation_id='createJuryEvaluation',
    url_name='jury_evaluate_create',
    response={201: SubmissionEvaluationResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse},
)
def create_jury_evaluation(request, payload: SubmissionEvaluationRequest):
    _require_evaluation_access(request)
    _check_tournament(assignment, payload.tournament_id)

    assignment = _get_assignment(request.auth, payload.assignment)
    
    if SubmissionEvaluation.objects.filter(assignment=payload.assignment).exists():
        raise HttpError(400, 'This submission is already evaluated.')

    evaluation = SubmissionEvaluation.objects.create(
        assignment=assignment,
        scores=_build_scores(assignment.submission.round, payload.scores),
        comment=payload.comment,
    )
    _after_evaluation_saved(evaluation, 'evaluation_created')

    return 201, SubmissionEvaluationResponse.model_validate(
        evaluation,
        from_attributes=True,
        context={"request": request},
    )


@router.get(
    '/jury-evaluations/{evaluation_id}',
    operation_id='getJuryEvaluation',
    url_name='jury_evaluate',
    response={200: SubmissionEvaluationResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def get_jury_evaluation(request, evaluation_id: int):
    _require_evaluation_access(request)

    evaluation = get_object_or_404(
        _own_evaluations(request.auth),
        pk=evaluation_id,
    )

    return SubmissionEvaluationResponse.model_validate(
        evaluation,
        from_attributes=True,
        context={"request": request},
    )


@router.patch(
    '/jury-evaluations/{evaluation_id}',
    operation_id='updateJuryEvaluation',
    url_name='jury_evaluate',
    response={
        200: SubmissionEvaluationResponse,
        400: ErrorResponse,
        401: ErrorResponse,
        403: ErrorResponse,
        404: ErrorResponse,
    },
)
def update_jury_evaluation(
    request,
    evaluation_id: int,
    payload: SubmissionEvaluationPatchRequest,
):
    _require_evaluation_access(request)

    evaluation = get_object_or_404(
        _own_evaluations(request.auth),
        pk=evaluation_id,
    )

    round = evaluation.assignment.submission.round
    round = evaluation.assignment.submission.round

    if round.status == Round.STATUS_EVALUATED:
        raise HttpError(
            400,
            'Cannot update evaluation after round evaluation is completed.',
        )
    
    data = payload.model_dump(exclude_unset=True)

    assignment = evaluation.assignment

    if data.get('scores') is not None:
        evaluation.scores = _build_scores(
            assignment.submission.round,
            data['scores'],
        )

    if 'comment' in data and data['comment'] is not None:
        evaluation.comment = data['comment']

    evaluation.save()

    _after_evaluation_saved(
        evaluation,
        'evaluation_updated',
    )

    return SubmissionEvaluationResponse.model_validate(
        evaluation,
        from_attributes=True,
        context={"request": request},
    )


@router.delete(
    '/jury-evaluations/{evaluation_id}',
    operation_id='deleteJuryEvaluation',
    url_name='jury_evaluate',
    response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def delete_jury_evaluation(request, evaluation_id: int):
    _require_evaluation_access(request)
    evaluation = get_object_or_404(_own_evaluations(request.auth), pk=evaluation_id)

    submission = evaluation.assignment.submission
    round_obj = submission.round
    deleted_id = evaluation.id
    evaluation.delete()

    emit_tournament_leaderboard_updated(
        tournament_id=round_obj.tournament_id,
        round_id=round_obj.id,
        reason='evaluation_deleted',
        submission_id=submission.id,
        evaluation_id=deleted_id,
    )
    return 204, None


# =============================================================================
# Admin: jury assignment
#
#   POST /rounds/{round_id}/jury-assignments   -> assign_jury_to_round
#   GET  /rounds/{round_id}/available-jury     -> list_available_jury
# =============================================================================

@router.post(
    '/rounds/{round_id}/jury-assignments',
    operation_id='assignJuryToRound',
    url_name='round_assign_jury',
    response={201: AssignJuryResponse, 400: ErrorResponse, 401: ErrorResponse,
              403: ErrorResponse, 404: ErrorResponse},
)
def assign_jury_to_round(request, round_id: int, payload: list[JuryAssignmentItemRequest]):
    _require_assignment_management(request)
    round_obj = get_object_or_404(Round, pk=round_id)

    submission_ids = [item.submission for item in payload]
    submissions = Submission.objects.in_bulk(submission_ids)
    missing = sorted(set(submission_ids) - set(submissions))
    if missing:
        raise HttpError(400, 'One or more submissions do not exist.')

    items = [
        {'submission': submissions[item.submission], 'jury': item.jury}
        for item in payload
    ]
    created_count = replace_round_jury_assignments(round_obj, items)

    return 201, AssignJuryResponse.model_validate({
        'status': 'Assignments replaced.',
        'created_assignments': created_count,
    })


@router.get(
    '/rounds/{round_id}/available-jury',
    operation_id='listAvailableJury',
    url_name='round_available_jury',
    response={200: list[AvailableJuryResponse], 400: ErrorResponse, 401: ErrorResponse,
              403: ErrorResponse, 404: ErrorResponse},
)
def list_available_jury(request, round_id: int, include_assigned: bool = True):
    _require_assignment_management(request)
    round_obj = get_object_or_404(Round, pk=round_id)

    return [
        AvailableJuryResponse.model_validate(
            item,
            from_attributes=True,
            context={"request": request},
        )
        for item in get_available_jury(
            round_obj=round_obj,
            include_assigned=include_assigned,
        )
    ]


# =============================================================================
# Leaderboards (any authenticated user)
#
#   GET /rounds/{round_id}/leaderboard            -> get_round_leaderboard
#   GET /tournaments/{tournament_id}/leaderboard  -> get_tournament_leaderboard_view
# =============================================================================

@router.get(
    '/rounds/{round_id}/leaderboard',
    operation_id='getRoundLeaderboard',
    url_name='round_leaderboard',
    response={200: RoundLeaderboardResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def get_round_leaderboard(request, round_id: int):
    round_obj = Round.objects.select_related('tournament').filter(id=round_id).first()
    if not round_obj:
        raise HttpError(404, 'Round not found.')

    rankings = get_leaderboard(round_id=round_id, requesting_user=request.auth)
    return {
        'round_id': round_id,
        'is_snapshot': round_obj.tournament.status == Tournament.STATUS_FINISHED,
        'rankings': rankings,
    }


@router.get(
    '/tournaments/{tournament_id}/leaderboard',
    operation_id='getTournamentLeaderboard',
    url_name="tournament_leaderboard",
    response={200: TournamentLeaderboardResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def get_tournament_leaderboard_view(request, tournament_id: int):
    tournament = Tournament.objects.filter(id=tournament_id).first()
    if not tournament:
        raise HttpError(404, 'Tournament not found.')

    if not Round.objects.filter(tournament_id=tournament_id).exists():
        raise HttpError(404, 'No rounds found for this tournament.')

    rankings = get_tournament_leaderboard(tournament_id=tournament_id, requesting_user=request.auth)
    return {
        'tournament_id': tournament_id,
        'is_snapshot': tournament.status == Tournament.STATUS_FINISHED,
        'rankings': rankings,
    }


# =============================================================================
# Passing status (admin)
#
#   GET /rounds/{round_id}/passing-status  -> get_round_passing_status
# =============================================================================

@router.get(
    '/rounds/{round_id}/passing-status',
    operation_id='getRoundPassingStatus',
    url_name="round_passing_status",
    response={200: RoundPassingStatusResponse, 400: ErrorResponse, 401: ErrorResponse,
              403: ErrorResponse, 404: ErrorResponse},
)
def get_round_passing_status(request, round_id: int):
    round_obj = get_object_or_404(Round.objects.select_related('tournament'), pk=round_id)

    if round_obj.status not in {Round.STATUS_SUBMISSION_CLOSED, Round.STATUS_EVALUATED}:
        raise HttpError(400, 'Round must be submission_closed or evaluated to check passing status.')

    result = compute_leaderboard(round_obj.id)
    team_ids = [row['team_id'] for row in result]

    registrations = {
        reg.team_id: reg
        for reg in TournamentTeamRegistration.objects.filter(
            tournament=round_obj.tournament,
            team_id__in=team_ids,
        )
    }

    passing_count = round_obj.passing_count
    results_list = []
    for row in result:
        reg = registrations.get(row['team_id'])
        results_list.append({
            'rank': row['rank'],
            'team_id': row['team_id'],
            'team_name': row['team_name'],
            'total_score': row['total_score'],
            'average_score': row['average_score'],
            'passed': passing_count is None or row['rank'] <= passing_count,
            'is_active': reg.is_active if reg else None,
            'disqualification_reason': reg.disqualification_reason if reg else None,
            'registration_id': reg.id if reg else None,
        })

    return {
        'round_id': round_obj.id,
        'round_name': round_obj.name,
        'passing_count': passing_count,
        'total_teams': len(result),
        'results': results_list,
    }