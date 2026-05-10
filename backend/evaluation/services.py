from django.db import transaction
from rest_framework.exceptions import ValidationError
from accounts.models import User
from tournaments.models import Round
from tournaments.models import TournamentTeamRegistration

from .models import JuryAssignment


@transaction.atomic
def replace_round_jury_assignments(round_obj, assignments_data):
    if round_obj.status != Round.STATUS_SUBMISSION_CLOSED:
        raise ValidationError({'status': 'Round must be submission_closed before assignment.'})

    round_submission_ids = set(round_obj.submissions.values_list('id', flat=True))
    payload_submission_ids = []
    jury_count_per_submission = set()
    all_jury_ids = set()

    for item in assignments_data:
        submission_id = item['submission'].id
        jury_ids = item['jury']
        payload_submission_ids.append(submission_id)

        if submission_id not in round_submission_ids:
            raise ValidationError({'submission': f'Submission {submission_id} does not belong to this round.'})

        if len(jury_ids) == 0:
            raise ValidationError({'jury': 'Each submission must have at least one jury member.'})
        if len(jury_ids) != len(set(jury_ids)):
            raise ValidationError({'jury': f'Duplicate jury ids found for submission {submission_id}.'})

        jury_count_per_submission.add(len(jury_ids))
        all_jury_ids.update(jury_ids)

    if len(payload_submission_ids) != len(set(payload_submission_ids)):
        raise ValidationError({'submission': 'Duplicate submission entries are not allowed.'})

    missing_submissions = round_submission_ids - set(payload_submission_ids)
    if missing_submissions:
        missing_text = ', '.join(str(item) for item in sorted(missing_submissions))
        raise ValidationError({'submission': f'Assignments are required for all round submissions. Missing: {missing_text}'})

    if len(jury_count_per_submission) != 1:
        raise ValidationError({'jury': 'Each submission must have the same number of jury members.'})

    jury_users = User.objects.filter(id__in=all_jury_ids, role='jury')
    found_jury_ids = set(jury_users.values_list('id', flat=True))
    missing_jury_ids = all_jury_ids - found_jury_ids
    if missing_jury_ids:
        missing_text = ', '.join(str(item) for item in sorted(missing_jury_ids))
        raise ValidationError({'jury': f'Invalid jury user ids or non-jury users: {missing_text}'})

    JuryAssignment.objects.filter(submission__round=round_obj).delete()
    new_assignments = []
    for item in assignments_data:
        submission_id = item['submission'].id
        for jury_id in item['jury']:
            new_assignments.append(JuryAssignment(submission_id=submission_id, jury_id=jury_id))

    if new_assignments:
        JuryAssignment.objects.bulk_create(new_assignments)

    return len(new_assignments)


def get_available_jury(*, round_obj, include_assigned=True):
    jury_queryset = User.objects.filter(role='jury').order_by('id')
    if include_assigned:
        return jury_queryset

    assigned_jury_ids = JuryAssignment.objects.filter(
        submission__round=round_obj
    ).values_list('jury_id', flat=True).distinct()
    return jury_queryset.exclude(id__in=assigned_jury_ids)


def try_auto_evaluate_round(round_obj):
    """Auto-mark a round as evaluated when all jury assignments have evaluations."""
    if round_obj.status != Round.STATUS_SUBMISSION_CLOSED:
        return

    total = JuryAssignment.objects.filter(submission__round=round_obj).count()
    if total == 0:
        return

    evaluated = JuryAssignment.objects.filter(
        submission__round=round_obj,
        evaluation__isnull=False,
    ).count()

    if total == evaluated:
        from tournaments.services import mark_round_evaluated
        mark_round_evaluated(round_obj)


def apply_passing_count(round_obj) -> dict:
    """
    Apply automatic elimination based on passing_count.
    """
    passing_count = round_obj.passing_count
    if passing_count is None:
        return {
            'applied': False,
            'passing_count': None,
            'total_teams': 0,
            'eliminated_team_ids': [],
            'passed_team_ids': [],
        }

    from evaluation.leaderboard_service import compute_leaderboard

    rankings = compute_leaderboard(round_obj.id)
    total_teams = len(rankings)
    if total_teams == 0:
        return {
            'applied': True,
            'passing_count': passing_count,
            'total_teams': 0,
            'eliminated_team_ids': [],
            'passed_team_ids': [],
        }

    passed_team_ids = [
        row['team_id']
        for row in rankings
        if row['rank'] <= passing_count
    ]
    eliminated_team_ids = [
        row['team_id']
        for row in rankings
        if row['rank'] > passing_count
    ]

    if eliminated_team_ids:
        TournamentTeamRegistration.objects.filter(
            tournament=round_obj.tournament,
            team_id__in=eliminated_team_ids,
            is_active=True,
        ).update(
            is_active=False,
            is_disqualified=False,
            disqualification_reason=f'Eliminated by rank in {round_obj.name}'
        )

    return {
        'applied': True,
        'passing_count': passing_count,
        'total_teams': total_teams,
        'eliminated_team_ids': eliminated_team_ids,
        'passed_team_ids': passed_team_ids,
    }
