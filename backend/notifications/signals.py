from django.dispatch import receiver
from .services import NotificationService
from teams.signals import (
    invitation_received,
    invitation_responded,
    join_request_received,
    join_request_responded,
    member_removed,
    member_left
)
from teams.models import TeamInvitation, TeamJoinRequest
from tournaments.signals import (
    tournament_team_registered,
    tournament_team_left,
    tournament_team_disqualified,
    round_started,
    round_submission_closed,
    round_evaluated,
    tournament_finished,
)
from evaluation.signals import jury_assignments_created
from tournaments.services import get_team_participant_ids


# ── Teams ──────────────────────────────────────────────────────────

@receiver(invitation_received)
def handle_invitation_received(sender, invitation, **kwargs):
    NotificationService.notify(
        recipients=[invitation.user],
        event_type='team_invitation_received',
        context={
            'team_name': invitation.team.name,
            'team_id': invitation.team.id,
            'invited_by': invitation.invited_by.username,
            'user_id': invitation.invited_by.id
        },
    )

@receiver(invitation_responded)
def handle_invitation_responded(sender, invitation, **kwargs):
    event_type = 'team_invitation_accepted' if invitation.status == TeamInvitation.STATUS_ACCEPTED else 'team_invitation_declined'
    NotificationService.notify(
        recipients=[invitation.team.captain],
        event_type=event_type,
        context={
            'team_name': invitation.team.name,
            'team_id': invitation.team.id,
            'user_name': invitation.user.username,
            'user_id': invitation.user.id
        },
    )

@receiver(join_request_received)
def handle_join_request_received(sender, join_request, **kwargs):
    NotificationService.notify(
        recipients=[join_request.team.captain],
        event_type='team_join_request_received',
        context={
            'team_name': join_request.team.name,
            'team_id': join_request.team.id,
            'user_name': join_request.user.username,
            'user_id': join_request.user.id
        },
    )

@receiver(join_request_responded)
def handle_join_request_responded(sender, join_request, **kwargs):
    event_type = 'team_join_request_accepted' if join_request.status == TeamJoinRequest.STATUS_ACCEPTED else 'team_join_request_declined'
    NotificationService.notify(
        recipients=[join_request.user],
        event_type=event_type,
        context={
            'team_name': join_request.team.name,
            'team_id': join_request.team.id
        },
    )

@receiver(member_removed)
def handle_member_removed(sender, team, user, **kwargs):
    NotificationService.notify(
        recipients=[user],
        event_type='team_member_removed',
        context={
            'team_name': team.name,
            'team_id': team.id
        },
    )

@receiver(member_left)
def handle_member_left(sender, team, user, **kwargs):
    NotificationService.notify(
        recipients=[team.captain],
        event_type='team_member_left',
        context={
            'team_name': team.name,
            'team_id': team.id,
            'user_name': user.username,
            'user_id': user.id
        },
    )


# ── Tournaments ────────────────────────────────────────────────────

def _get_tournament_participants(team, tournament):
    """Return User instances for all team members (captain + members)."""
    from accounts.models import User
    participant_ids = get_team_participant_ids(team=team)
    return list(User.objects.filter(id__in=participant_ids))


@receiver(tournament_team_registered)
def handle_tournament_team_registered(sender, tournament, team, actor, **kwargs):
    recipients = _get_tournament_participants(team, tournament)
    NotificationService.notify(
        recipients=recipients,
        event_type='tournament_team_registered',
        context={
            'team_name': team.name,
            'team_id': team.id,
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
        },
    )


@receiver(tournament_team_left)
def handle_tournament_team_left(sender, tournament, team, actor, **kwargs):
    recipients = _get_tournament_participants(team, tournament)
    NotificationService.notify(
        recipients=recipients,
        event_type='tournament_team_left',
        context={
            'team_name': team.name,
            'team_id': team.id,
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
        },
    )


@receiver(tournament_team_disqualified)
def handle_tournament_team_disqualified(sender, tournament, team, reason, **kwargs):
    recipients = _get_tournament_participants(team, tournament)
    NotificationService.notify(
        recipients=recipients,
        event_type='tournament_team_disqualified',
        context={
            'team_name': team.name,
            'team_id': team.id,
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
            'reason': reason or 'No reason provided',
        },
    )


@receiver(round_started)
def handle_round_started(sender, round_obj, **kwargs):
    """Notify all actively registered teams when a round starts."""
    from accounts.models import User
    from tournaments.models import TournamentTeamRegistration
    tournament = round_obj.tournament

    registered_team_ids = TournamentTeamRegistration.objects.filter(
        tournament=tournament,
        is_active=True,
    ).values_list('team_id', flat=True)

    from teams.models import TeamMember
    member_ids = set(
        TeamMember.objects.filter(
            team_id__in=registered_team_ids
        ).values_list('user_id', flat=True)
    )
    captain_ids = set(
        TournamentTeamRegistration.objects.filter(
            tournament=tournament,
            is_active=True,
        ).select_related('team').values_list('team__captain_id', flat=True)
    )
    all_participant_ids = member_ids | captain_ids

    recipients = list(User.objects.filter(id__in=all_participant_ids))
    NotificationService.notify(
        recipients=recipients,
        event_type='tournament_round_started',
        context={
            'round_name': round_obj.name or round_obj.default_name,
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
        },
    )


@receiver(round_submission_closed)
def handle_round_submission_closed(sender, round_obj, **kwargs):
    """Notify all active participants when a round's submissions are closed."""
    from accounts.models import User
    from tournaments.models import TournamentTeamRegistration
    from teams.models import TeamMember
    tournament = round_obj.tournament

    registered_team_ids = TournamentTeamRegistration.objects.filter(
        tournament=tournament,
        is_active=True,
    ).values_list('team_id', flat=True)

    member_ids = set(
        TeamMember.objects.filter(team_id__in=registered_team_ids).values_list('user_id', flat=True)
    )
    captain_ids = set(
        TournamentTeamRegistration.objects.filter(
            tournament=tournament, is_active=True,
        ).select_related('team').values_list('team__captain_id', flat=True)
    )
    all_participant_ids = member_ids | captain_ids

    recipients = list(User.objects.filter(id__in=all_participant_ids))
    NotificationService.notify(
        recipients=recipients,
        event_type='tournament_round_submission_closed',
        context={
            'round_name': round_obj.name or round_obj.default_name,
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
        },
    )


@receiver(round_evaluated)
def handle_round_evaluated(sender, round_obj, eliminated_team_ids, **kwargs):
    """Notify active participants about results. Also notify eliminated teams."""
    from accounts.models import User
    from tournaments.models import TournamentTeamRegistration
    from teams.models import TeamMember, Team
    tournament = round_obj.tournament
    round_name = round_obj.name or round_obj.default_name

    # Active participants: notify about results
    registered_team_ids = list(
        TournamentTeamRegistration.objects.filter(
            tournament=tournament, is_active=True,
        ).values_list('team_id', flat=True)
    )
    member_ids = set(
        TeamMember.objects.filter(team_id__in=registered_team_ids).values_list('user_id', flat=True)
    )
    captain_ids = set(
        TournamentTeamRegistration.objects.filter(
            tournament=tournament, is_active=True,
        ).select_related('team').values_list('team__captain_id', flat=True)
    )
    all_active_ids = member_ids | captain_ids
    active_recipients = list(User.objects.filter(id__in=all_active_ids))

    NotificationService.notify(
        recipients=active_recipients,
        event_type='tournament_round_evaluated',
        context={
            'round_name': round_name,
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
        },
    )

    # Eliminated teams: notify about elimination per team
    if eliminated_team_ids:
        for team in Team.objects.filter(id__in=eliminated_team_ids):
            team_recipients = _get_tournament_participants(team, tournament)
            NotificationService.notify(
                recipients=team_recipients,
                event_type='tournament_round_eliminated',
                context={
                    'team_name': team.name,
                    'round_name': round_name,
                    'tournament_name': tournament.name,
                    'tournament_id': tournament.id,
                },
            )


@receiver(tournament_finished)
def handle_tournament_finished(sender, tournament, **kwargs):
    """Notify all tournament participants (including former) when it finishes."""
    from accounts.models import User
    from tournaments.models import TournamentTeamRegistration
    from teams.models import TeamMember

    all_registered_team_ids = TournamentTeamRegistration.objects.filter(
        tournament=tournament,
    ).values_list('team_id', flat=True)

    member_ids = set(
        TeamMember.objects.filter(team_id__in=all_registered_team_ids).values_list('user_id', flat=True)
    )
    captain_ids = set(
        TournamentTeamRegistration.objects.filter(
            tournament=tournament,
        ).select_related('team').values_list('team__captain_id', flat=True)
    )
    all_participant_ids = member_ids | captain_ids

    recipients = list(User.objects.filter(id__in=all_participant_ids))
    NotificationService.notify(
        recipients=recipients,
        event_type='tournament_finished',
        context={
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
        },
    )


# ── Evaluation ─────────────────────────────────────────────────────

@receiver(jury_assignments_created)
def handle_jury_assignments_created(sender, round_obj, jury_users, **kwargs):
    """Notify each jury member when they are assigned to evaluate a round."""
    tournament = round_obj.tournament
    NotificationService.notify(
        recipients=jury_users,
        event_type='jury_assignment_created',
        context={
            'round_name': round_obj.name or round_obj.default_name,
            'tournament_name': tournament.name,
            'tournament_id': tournament.id,
        },
    )
