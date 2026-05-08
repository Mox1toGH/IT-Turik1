from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from teams.models import TeamMember

from .models import Round, Tournament, TournamentTeamRegistration


def _set_tournament_finished_if_all_rounds_evaluated(*, tournament):
    if tournament.status != Tournament.STATUS_RUNNING:
        return False

    has_pending_rounds = tournament.rounds.exclude(status=Round.STATUS_EVALUATED).exists()
    if has_pending_rounds:
        return False

    tournament.status = Tournament.STATUS_FINISHED
    tournament.save(update_fields=['status', 'updated_at'])
    last_round = tournament.rounds.order_by('-start_date', '-id').first()
    if last_round:
        from evaluation.leaderboard_service import save_leaderboard_snapshot
        save_leaderboard_snapshot(tournament_id=tournament.id, round_id=last_round.id)
    return True


@transaction.atomic
def start_registration(tournament):
    if tournament.status != Tournament.STATUS_DRAFT:
        raise ValidationError({'status': 'Only draft tournaments can be moved to registration.'})

    tournament.status = Tournament.STATUS_REGISTRATION
    tournament.save(update_fields=['status', 'updated_at'])
    return tournament


@transaction.atomic
def start_round(round_obj):
    now = timezone.now()
    round_obj = Round.objects.select_for_update().select_related('tournament').get(id=round_obj.id)
    tournament = round_obj.tournament

    if round_obj.status != Round.STATUS_DRAFT:
        raise ValidationError({'status': 'Only draft rounds can be started.'})

    if round_obj.start_date > now:
        raise ValidationError({'start_date': 'Round start_date has not been reached yet.'})

    if round_obj.end_date <= now:
        raise ValidationError({'end_date': 'Round already passed its deadline.'})

    if tournament.status not in {Tournament.STATUS_REGISTRATION, Tournament.STATUS_RUNNING}:
        raise ValidationError({'tournament': 'Tournament must be in registration or running status.'})

    is_first_round = not Round.objects.filter(
        tournament=tournament,
        start_date__lt=round_obj.start_date,
    ).exists()
    if is_first_round and tournament.status != Tournament.STATUS_REGISTRATION:
        raise ValidationError({'tournament': 'First round can start only from registration status.'})

    if not is_first_round:
        prev_round = (
            Round.objects.filter(tournament=tournament, start_date__lt=round_obj.start_date)
            .order_by('-start_date')
            .only('status')
            .first()
        )
        if prev_round is None or prev_round.status != Round.STATUS_EVALUATED:
            raise ValidationError({'status': 'Previous round must be evaluated before starting the next round.'})

    if Round.objects.filter(tournament=tournament, status=Round.STATUS_ACTIVE).exclude(id=round_obj.id).exists():
        raise ValidationError({'status': 'Another round is already active for this tournament.'})

    round_obj.status = Round.STATUS_ACTIVE
    round_obj.save(update_fields=['status', 'updated_at'])

    if tournament.status != Tournament.STATUS_RUNNING:
        tournament.status = Tournament.STATUS_RUNNING
        tournament.save(update_fields=['status', 'updated_at'])

    return round_obj


@transaction.atomic
def close_submissions_on_round(round_obj):
    round_obj = Round.objects.select_for_update().get(id=round_obj.id)

    if round_obj.status != Round.STATUS_ACTIVE:
        raise ValidationError({'status': 'Only active rounds can have their submissions closed.'})

    round_obj.status = Round.STATUS_SUBMISSION_CLOSED
    round_obj.save(update_fields=['status', 'updated_at'])

    return round_obj


@transaction.atomic
def mark_round_evaluated(round_obj):
    round_obj = Round.objects.select_for_update().select_related('tournament').get(id=round_obj.id)
    tournament = round_obj.tournament

    if round_obj.status != Round.STATUS_SUBMISSION_CLOSED:
        raise ValidationError({'status': 'Round must be submission_closed before evaluation.'})

    round_obj.status = Round.STATUS_EVALUATED
    round_obj.save(update_fields=['status', 'updated_at'])

    _set_tournament_finished_if_all_rounds_evaluated(tournament=tournament)

    return round_obj


@transaction.atomic
def sync_time_based_statuses(reference_time=None):
    now = reference_time or timezone.now()

    active_rounds_to_close = Round.objects.filter(
        status=Round.STATUS_ACTIVE,
        end_date__lte=now,
    )
    updated_round_ids = list(active_rounds_to_close.values_list('id', flat=True))
    if updated_round_ids:
        active_rounds_to_close.update(status=Round.STATUS_SUBMISSION_CLOSED, updated_at=now)

    running_tournaments = Tournament.objects.filter(status=Tournament.STATUS_RUNNING).prefetch_related('rounds')
    for tournament in running_tournaments:
        _set_tournament_finished_if_all_rounds_evaluated(tournament=tournament)

    return {
        'closed_round_ids': updated_round_ids,
    }


def get_team_participant_ids(*, team):
    participant_ids = set(
        TeamMember.objects.filter(team=team).values_list('user_id', flat=True)
    )
    participant_ids.add(team.captain_id)
    return participant_ids


def ensure_team_registered_for_tournament(*, tournament, team):
    if TournamentTeamRegistration.objects.filter(tournament=tournament, team=team, is_active=True).exists():
        return
    raise ValidationError({'team': 'Team must be registered and active for this tournament.'})


@transaction.atomic
def register_team_for_tournament(*, tournament, team, actor):
    if tournament.status != Tournament.STATUS_REGISTRATION:
        raise ValidationError({'tournament': 'Tournament is not open for team registration.'})

    if team.captain_id != actor.id:
        raise ValidationError({'team': 'Only the team owner can register this team for a tournament.'})

    if TournamentTeamRegistration.objects.filter(tournament=tournament, team=team).exists():
        raise ValidationError({'team': 'This team is already registered for the tournament.'})

    participant_ids = get_team_participant_ids(team=team)
    participant_count = len(participant_ids)
    if tournament.min_team_members and participant_count < tournament.min_team_members:
        raise ValidationError(
            {'team': f'Team must have at least {tournament.min_team_members} members for this tournament.'}
        )

    if tournament.max_teams is not None:
        current_registered_count = TournamentTeamRegistration.objects.filter(tournament=tournament).count()
        if current_registered_count >= tournament.max_teams:
            raise ValidationError({'tournament': 'Tournament registration limit has been reached.'})

    already_registered = TournamentTeamRegistration.objects.filter(
        team=team,
        is_active=True,
        tournament__status__in=[
            Tournament.STATUS_REGISTRATION,
            Tournament.STATUS_RUNNING,
        ],
    ).exclude(tournament=tournament).exists()

    if already_registered:
        raise ValidationError({
            'team': 'This team is already participating in another tournament.'
        })

    conflicting = (
        TeamMember.objects.filter(
            team__tournament_registrations__tournament__status__in=[
                Tournament.STATUS_REGISTRATION,
                Tournament.STATUS_RUNNING,
            ],
            team__tournament_registrations__is_active=True,
            user_id__in=participant_ids,
        )
        .exclude(team=team)
        .select_related('user')
    )
    if conflicting.exists():
        emails = ', '.join(m.user.email for m in conflicting)
        raise ValidationError({
            'team': f'Cannot register. The following members are already participating in another tournament: {emails}'
        })

    return TournamentTeamRegistration.objects.create(
        tournament=tournament,
        team=team,
        created_by=actor,
    )


@transaction.atomic
def delete_round(round_obj):
    round_obj = Round.objects.select_for_update().select_related('tournament').get(id=round_obj.id)
    tournament = round_obj.tournament

    rounds_count = Round.objects.filter(tournament=tournament).count()
    if rounds_count <= 1:
        raise ValidationError({'round': 'Cannot delete the last remaining round.'})
    round_obj.delete()
    tournament.save(update_fields=['updated_at'])
    return tournament


