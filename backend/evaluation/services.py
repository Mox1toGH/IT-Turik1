from django.db import transaction
from rest_framework.exceptions import ValidationError
from accounts.models import User
from tournaments.models import Round
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
