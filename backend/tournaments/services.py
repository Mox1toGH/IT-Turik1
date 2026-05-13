import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from teams.models import TeamMember

from .models import Round, Submission, Tournament, TournamentTeamRegistration


logger = logging.getLogger(__name__)


def _get_tournament_team_ranks(*, tournament):
    from evaluation.models import LeaderboardEntry

    leaderboard_entries = LeaderboardEntry.objects.filter(
        tournament=tournament,
        round__isnull=True,
    ).only('team_id', 'rank')
    return {
        entry.team_id: str(entry.rank)
        for entry in leaderboard_entries
        if entry.team_id and entry.rank is not None
    }


def _get_tournament_participant_team_map(*, tournament):
    submitted_team_ids = set(
        Submission.objects.filter(round__tournament=tournament).values_list('team_id', flat=True)
    )

    registrations = (
        TournamentTeamRegistration.objects.filter(
            tournament=tournament,
            is_disqualified=False,
        )
        .select_related('team')
        .order_by('id')
    )

    participant_team_map = {}
    for registration in registrations:
        team = registration.team
        if team is None:
            continue

        is_participant = registration.is_active or team.id in submitted_team_ids
        if not is_participant:
            continue

        for participant_id in get_team_participant_ids(team=team):
            # One certificate per user per tournament.
            participant_team_map.setdefault(participant_id, team.id)

    return participant_team_map


def _issue_tournament_certificates_and_notify(*, tournament):
    from accounts.models import User
    from certificates.models import Certificate
    from certificates.serializers import CertificateSerializer
    from notifications.services import NotificationService

    try:
        participant_team_map = _get_tournament_participant_team_map(tournament=tournament)
        if not participant_team_map:
            return

        participant_ids = list(participant_team_map.keys())
        existing_user_ids = set(
            Certificate.objects.filter(
                tournament=tournament,
                user_id__in=participant_ids,
            ).values_list('user_id', flat=True)
        )
        team_ranks = _get_tournament_team_ranks(tournament=tournament)

        created_user_ids = []
        for user_id, team_id in participant_team_map.items():
            if user_id in existing_user_ids:
                continue

            serializer = CertificateSerializer(
                data={
                    'user': user_id,
                    'team': team_id,
                    'tournament': tournament.id,
                    'placement': team_ranks.get(team_id, 'Participant'),
                }
            )
            if not serializer.is_valid():
                logger.warning(
                    'Failed to auto-create certificate for tournament_id=%s user_id=%s: %s',
                    tournament.id,
                    user_id,
                    serializer.errors,
                )
                continue

            serializer.save()
            created_user_ids.append(user_id)

        if not created_user_ids:
            return

        recipients = list(User.objects.filter(id__in=created_user_ids))
        NotificationService.notify(
            recipients=recipients,
            event_type='tournament_certificate_issued',
            context={
                'tournament_name': tournament.name,
            },
        )
    except Exception:
        logger.exception(
            'Failed to auto-issue certificates for tournament_id=%s',
            tournament.id,
        )


@transaction.atomic
def send_tournament_certificates(*, tournament, template_id, mode='missing'):
    from accounts.models import User
    from certificates.models import Certificate, CertificateTemplate
    from certificates.serializers import CertificateSerializer
    from notifications.services import NotificationService

    template = CertificateTemplate.objects.filter(id=template_id).first()
    if template is None:
        raise ValidationError({'template_id': 'Certificate template not found.'})

    participant_team_map = _get_tournament_participant_team_map(tournament=tournament)
    if not participant_team_map:
        return {
            'created_count': 0,
            'skipped_count': 0,
            'notification_count': 0,
        }

    participant_ids = list(participant_team_map.keys())
    existing_qs = Certificate.objects.filter(
        tournament=tournament,
        user_id__in=participant_ids,
    )
    existing_user_ids = set(existing_qs.values_list('user_id', flat=True))
    if mode not in {'missing', 'resend'}:
        raise ValidationError({'mode': 'Mode must be either "missing" or "resend".'})
    team_ranks = _get_tournament_team_ranks(tournament=tournament)

    created_user_ids = []
    skipped_count = 0
    for user_id, team_id in participant_team_map.items():
        if mode == 'missing' and user_id in existing_user_ids:
            skipped_count += 1
            continue

        serializer = CertificateSerializer(
            data={
                'user': user_id,
                'team': team_id,
                'tournament': tournament.id,
                'placement': team_ranks.get(team_id, 'Participant'),
                'template': template.id,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        created_user_ids.append(user_id)

    notification_count = 0
    if created_user_ids:
        recipients = list(User.objects.filter(id__in=created_user_ids))
        NotificationService.notify(
            recipients=recipients,
            event_type='tournament_certificate_issued',
            context={'tournament_name': tournament.name},
        )
        notification_count = len(recipients)

    return {
        'created_count': len(created_user_ids),
        'skipped_count': skipped_count,
        'notification_count': notification_count,
    }


def get_tournament_certificate_delivery_status(*, tournament):
    from certificates.models import Certificate

    participant_team_map = _get_tournament_participant_team_map(tournament=tournament)
    participant_ids = list(participant_team_map.keys())
    existing_count = 0
    if participant_ids:
        existing_count = Certificate.objects.filter(
            tournament=tournament,
            user_id__in=participant_ids,
        ).count()
    return {
        'participants_count': len(participant_ids),
        'existing_count': existing_count,
        'missing_count': max(len(participant_ids) - existing_count, 0),
    }


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

    from evaluation.services import apply_passing_count
    apply_passing_count(round_obj)

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

    existing_registration = TournamentTeamRegistration.objects.filter(
        tournament=tournament,
        team=team,
    ).first()
    if existing_registration and existing_registration.is_active:
        raise ValidationError({'team': 'This team is already registered for the tournament.'})

    participant_ids = get_team_participant_ids(team=team)
    participant_count = len(participant_ids)
    if tournament.min_team_members and participant_count < tournament.min_team_members:
        raise ValidationError(
            {'team': f'Team must have at least {tournament.min_team_members} members for this tournament.'}
        )

    if tournament.max_teams is not None:
        current_registered_count = TournamentTeamRegistration.objects.filter(
            tournament=tournament,
            is_active=True,
        ).count()
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

    if existing_registration:
        existing_registration.is_active = True
        existing_registration.created_by = actor
        existing_registration.save(update_fields=['is_active', 'created_by'])
        return existing_registration

    return TournamentTeamRegistration.objects.create(tournament=tournament, team=team, created_by=actor)


@transaction.atomic
def leave_team_from_tournament(*, tournament, team, actor):
    if team.captain_id != actor.id:
        raise ValidationError({'team': 'Only the team owner can remove this team from a tournament.'})

    registration = TournamentTeamRegistration.objects.filter(
        tournament=tournament,
        team=team,
        is_active=True,
    ).first()
    if registration is None:
        raise ValidationError({'team': 'This team is not actively registered for this tournament.'})

    registration.is_active = False
    registration.save(update_fields=['is_active'])
    return registration


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


