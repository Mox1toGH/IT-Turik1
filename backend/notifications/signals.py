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
