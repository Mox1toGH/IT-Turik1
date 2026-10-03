import logging
import re

from django.db import transaction
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import File, Router
from ninja.files import UploadedFile

from accounts.models import User
from backend.auth import JWTAuth
from backend.permissions import is_platform_admin

from .models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from backend.schemas import ErrorResponse
from backend.errors import raise_api_error
from http import HTTPStatus
from .schemas import (
    DetailResponse,
    InviteMemberRequest,
    TeamBannerResponse,
    TeamCreateRequest,
    TeamInvitationInboxResponse,
    TeamInvitationResponse,
    TeamJoinRequestResponse,
    TeamResponse,
    TeamUpdateRequest,
)
from .services import assert_can_remove_member, assert_team_not_in_active_tournament
from .signals import (
    invitation_received,
    invitation_responded,
    join_request_received,
    join_request_responded,
    member_left,
    member_removed,
)

logger = logging.getLogger(__name__)

router = Router(tags=['teams'], auth=JWTAuth(),)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def get_team_queryset():
    return (
        Team.objects.select_related('captain')
        .prefetch_related(
            'members',
            Prefetch(
                'invitations',
                queryset=TeamInvitation.objects.select_related('user', 'invited_by').order_by('-created_at'),
            ),
            Prefetch(
                'join_requests',
                queryset=TeamJoinRequest.objects.select_related('user', 'reviewed_by').order_by('-created_at'),
            ),
        )
        .order_by('id')
    )


def is_team_member(team, user):
    if team.captain_id == user.id:
        return True
    return any(member.id == user.id for member in team.members.all())


def get_accessible_team(request, pk):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.is_public or is_team_member(team, request.auth) or is_platform_admin(request.auth):
        return team
    logger.warning(
        'Access denied to private team',
        extra={'team_id': pk, 'user_id': request.auth.id},
    )
    raise_api_error(HTTPStatus.FORBIDDEN, 'You do not have access to this private team.')


def assert_can_create_team(user):
    if is_platform_admin(user) or user.role != 'team':
        logger.warning(
            'Team creation not permitted',
            extra={'user_id': user.id, 'role': user.role},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'You do not have permission to create a team.')


def normalize_telegram(value: str) -> str:
    normalized = value.strip().lstrip('@')
    if not normalized:
        return ''
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{4,31}', normalized):
        logger.warning('Invalid telegram username format')
        raise_api_error(
            HTTPStatus.BAD_REQUEST,
            'Telegram username must be 5-32 chars, start with a letter, and contain only letters, digits, or _.',
        )
    return normalized


def normalize_discord(value: str) -> str:
    normalized = value.strip().lstrip('@')
    if not normalized:
        return ''
    if not re.fullmatch(r'(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?', normalized):
        logger.warning('Invalid discord username format')
        raise_api_error(
            HTTPStatus.BAD_REQUEST,
            'Discord username must be 2-32 chars and may contain letters, digits, ".", "_" and optional #1234.',
        )
    return normalized


def validate_member_ids(value):
    if not value:
        return []
    unique_ids = sorted(set(value))
    existing_ids = set(User.objects.filter(id__in=unique_ids).values_list('id', flat=True))
    missing_ids = [user_id for user_id in unique_ids if user_id not in existing_ids]
    if missing_ids:
        logger.warning('Unknown member IDs', extra={'missing_ids': missing_ids})
        raise_api_error(HTTPStatus.BAD_REQUEST, f'Users not found: {missing_ids}')
    return unique_ids


def clear_invitation_states_for_member(*, team, user=None, user_id=None):
    target_user_id = user_id or getattr(user, 'id', None)
    if not target_user_id:
        return
    deleted, _ = TeamInvitation.objects.filter(team=team, user_id=target_user_id).delete()
    logger.debug(
        'Cleared invitations',
        extra={'team_id': team.id, 'user_id': target_user_id, 'deleted_count': deleted},
    )


def clear_join_request_states_for_member(*, team, user=None, user_id=None):
    target_user_id = user_id or getattr(user, 'id', None)
    if not target_user_id:
        return
    deleted, _ = TeamJoinRequest.objects.filter(team=team, user_id=target_user_id).delete()
    logger.debug(
        'Cleared join requests',
        extra={'team_id': team.id, 'user_id': target_user_id, 'deleted_count': deleted},
    )


def invite_user_to_team(*, team, user, invited_by):
    """Invite a user to a team.

    Returns (invitation, newly_invited). newly_invited is True when the user just
    became invited (new invitation, or a previously accepted/declined one was
    re-opened) and False when an invitation was already pending, so callers should
    only send the "invitation received" signal when it is True.
    Returns (None, False) if the user is already a member.
    """
    assert_team_not_in_active_tournament(team)

    if TeamMember.objects.filter(team=team, user=user).exists():
        logger.debug(
            'Invite skipped, already a member',
            extra={'team_id': team.id, 'user_id': user.id},
        )
        return None, False

    with transaction.atomic():
        invitation = (
            TeamInvitation.objects.select_for_update()
            .filter(team=team, user=user)
            .order_by('-created_at', '-id')
            .first()
        )

        if invitation is None:
            invitation = TeamInvitation.objects.create(
                team=team,
                user=user,
                invited_by=invited_by,
                status=TeamInvitation.STATUS_INVITED,
            )
            created = True
        elif invitation.status == TeamInvitation.STATUS_INVITED:
            # Already pending: nothing new to notify about.
            created = False
        else:
            # Previously accepted/declined: re-open the same invitation.
            invitation.status = TeamInvitation.STATUS_INVITED
            invitation.responded_at = None
            invitation.invited_by = invited_by
            invitation.save(update_fields=['status', 'responded_at', 'invited_by', 'updated_at'])
            created = True

        declined = TeamJoinRequest.objects.filter(
            team=team,
            user=user,
            status=TeamJoinRequest.STATUS_PENDING,
        ).update(
            status=TeamJoinRequest.STATUS_DECLINED,
            reviewed_by=invited_by,
            reviewed_at=timezone.now(),
        )

    logger.info(
        'User invited to team',
        extra={
            'team_id': team.id,
            'user_id': user.id,
            'invited_by': invited_by.id,
            'invitation_id': invitation.id,
            'newly_invited': created,
            'auto_declined_requests': declined,
        },
    )

    return invitation, created


# --------------------------------------------------------------------------
# Teams
# --------------------------------------------------------------------------

@router.get(
    '/',
    operation_id='listTeams',
    url_name='teams',
    response={200: list[TeamResponse], 401: ErrorResponse},
)
def list_teams(request):
    user = request.auth
    logger.debug('Listing teams', extra={'user_id': user.id})
    queryset = get_team_queryset()
    if not is_platform_admin(user):
        queryset = queryset.filter(
            Q(is_public=True) | Q(captain_id=user.id) | Q(team_members__user_id=user.id)
        ).distinct()

    return list(queryset.iterator(chunk_size=100))


@router.post(
    '/',
    operation_id='createTeam',
    url_name='listTeams',
    response={201: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse},
)
def create_team(request, payload: TeamCreateRequest):
    user = request.auth
    logger.info(
        'Creating team',
        extra={'team_name': payload.name, 'user_id': user.id},
    )
    assert_can_create_team(user)

    if Team.objects.filter(name=payload.name).exists():
        logger.warning(
            'Team creation rejected, name taken',
            extra={'team_name': payload.name, 'user_id': user.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Team with this name already exists.')

    contact_telegram = normalize_telegram(payload.contact_telegram)
    contact_discord = normalize_discord(payload.contact_discord)
    member_ids = validate_member_ids(payload.member_ids)
    new_invitations = []

    with transaction.atomic():
        team = Team.objects.create(
            captain=user,
            name=payload.name,
            email=payload.email,
            is_public=payload.is_public,
            organization=payload.organization,
            contact_telegram=contact_telegram,
            contact_discord=contact_discord,
        )
        TeamMember.objects.get_or_create(team=team, user=user)

        for invited_user in User.objects.filter(id__in=member_ids).exclude(id=user.id):
            invitation, newly_invited = invite_user_to_team(team=team, user=invited_user, invited_by=user)
            if invitation and newly_invited:
                new_invitations.append(invitation)

    for invitation in new_invitations:
        invitation_received.send(sender=create_team, invitation=invitation)

    logger.info(
        'Team created',
        extra={
            'team_id': team.id,
            'captain_id': user.id,
            'is_public': team.is_public,
            'invited_count': len(member_ids),
        },
    )

    team = get_object_or_404(get_team_queryset(), pk=team.pk)
    return 201, TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.get(
    '/{int:pk}',
    operation_id='getTeam',
    url_name='team_detail',
    response={200: TeamResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def get_team(request, pk: int):
    logger.debug('Fetching team', extra={'team_id': pk, 'user_id': request.auth.id})
    team = get_accessible_team(request, pk)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


def apply_team_update(request, pk: int, payload: TeamUpdateRequest):
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        logger.warning(
            'Team update rejected, not captain',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(403, 'Only captain can modify this team.')

    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    member_ids = data.pop('member_ids', None)
    logger.info(
        'Updating team',
        extra={
            'team_id': pk,
            'user_id': request.auth.id,
            'fields': sorted(data.keys()),
            'invite_members': member_ids is not None,
        },
    )

    if 'name' in data or 'is_public' in data:
        assert_team_not_in_active_tournament(team)

    if 'contact_telegram' in data:
        data['contact_telegram'] = normalize_telegram(data['contact_telegram'])
    if 'contact_discord' in data:
        data['contact_discord'] = normalize_discord(data['contact_discord'])
    if member_ids is not None:
        member_ids = validate_member_ids(member_ids)

    new_invitations = []

    with transaction.atomic():
        for field, value in data.items():
            setattr(team, field, value)
        team.save()

        if member_ids is not None:
            for invited_user in User.objects.filter(id__in=member_ids).exclude(id=team.captain_id):
                invitation, newly_invited = invite_user_to_team(team=team, user=invited_user, invited_by=request.auth)
                if invitation and newly_invited:
                    new_invitations.append(invitation)

    for invitation in new_invitations:
        invitation_received.send(sender=apply_team_update, invitation=invitation)

    logger.info('Team updated', extra={'team_id': team.id, 'user_id': request.auth.id})

    team = get_object_or_404(get_team_queryset(), pk=team.pk)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})

@router.patch(
    '/{int:pk}',
    operation_id='updateTeam',
    url_name='team_detail',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def update_team(request, pk: int, payload: TeamUpdateRequest):
    return apply_team_update(request, pk, payload)


@router.delete(
    '/{int:pk}',
    operation_id='deleteTeam',
    url_name='team_detail',
    response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def delete_team(request, pk: int):
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        logger.warning(
            'Team delete rejected, not captain',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only captain can modify this team.')
    assert_team_not_in_active_tournament(team)
    team.delete()
    logger.info('Team deleted', extra={'team_id': pk, 'user_id': request.auth.id})
    return 204, None


# --------------------------------------------------------------------------
# Banner
# --------------------------------------------------------------------------

def apply_banner_upload(request, pk: int, banner: UploadedFile):
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        logger.warning(
            'Banner upload rejected, not captain',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only captain can modify this team banner.')
    if not (banner.content_type or '').startswith('image/'):
        logger.warning(
            'Banner upload rejected, not an image',
            extra={
                'team_id': pk,
                'user_id': request.auth.id,
                'content_type': banner.content_type,
            },
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Upload a valid image.')

    team.banner = banner
    team.save(update_fields=['banner'])
    team.refresh_from_db()
    logger.info(
        'Team banner updated',
        extra={
            'team_id': pk,
            'user_id': request.auth.id,
            'file_name': banner.name,
            'file_size': banner.size,
        },
    )
    return TeamBannerResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.patch(
    '/{int:pk}/banner',
    operation_id='teamBannerPartialUpdate',
    url_name='team_banner',
    response={200: TeamBannerResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def update_team_banner(request, pk: int, banner: UploadedFile = File(...)):
    return apply_banner_upload(request, pk, banner)


@router.delete(
    '/{int:pk}/banner',
    operation_id='deleteTeamBanner',
    url_name='team_banner',
    response={200: TeamResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def delete_team_banner(request, pk: int):
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        logger.warning(
            'Banner delete rejected, not captain',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only captain can modify this team banner.')

    if team.banner:
        team.banner.delete(save=False)
        team.banner = None
        team.save(update_fields=['banner'])
        logger.info('Team banner deleted', extra={'team_id': pk, 'user_id': request.auth.id})
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


# --------------------------------------------------------------------------
# Members
# --------------------------------------------------------------------------

@router.post(
    '/{int:pk}/members/invite',
    operation_id='inviteMemberToTeam',
    url_name='team_members',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def invite_member_to_team(request, pk: int, payload: InviteMemberRequest):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id:
        logger.warning(
            'Invite rejected, not captain',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(403, 'Only captain can manage members.')

    logger.info(
        'Invite requested',
        extra={
            'team_id': pk,
            'target_user_id': payload.user_id,
            'user_id': request.auth.id,
        },
    )
    assert_team_not_in_active_tournament(team)

    if not payload.user_id:
        logger.warning('Invite rejected, missing user_id', extra={'team_id': pk})
        raise_api_error(HTTPStatus.BAD_REQUEST, 'user_id is required.')

    user = get_object_or_404(User, id=payload.user_id)
    if user.id == team.captain_id:
        logger.warning(
            'Invite rejected, target is captain',
            extra={'team_id': pk, 'target_user_id': user.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Captain is already on the team.')

    if TeamMember.objects.filter(team=team, user=user).exists():
        logger.warning(
            'Invite rejected, already a member',
            extra={'team_id': pk, 'target_user_id': user.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'User is already a team member.')

    invitation, created = invite_user_to_team(team=team, user=user, invited_by=request.auth)
    if not invitation:
        logger.warning('Invite failed', extra={'team_id': pk, 'target_user_id': user.id})
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Unable to invite this user.')

    if created:
        invitation_received.send(sender=invite_member_to_team, invitation=invitation)
    else:
        logger.debug(
            'Invite already pending, no notification sent',
            extra={'team_id': pk, 'target_user_id': user.id},
        )

    team = get_object_or_404(get_team_queryset(), pk=pk)
    return TeamResponse.model_validate(
        team, from_attributes=True, context={'request': request}
    )


@router.delete(
    '/{int:pk}/members/{int:user_id}',
    operation_id='removeMemberFromTeam',
    url_name='team_member_detail',
    response={204: None, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def remove_member_from_team(request, pk: int, user_id: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id:
        logger.warning(
            'Member removal rejected, not captain',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only captain can manage members.')

    logger.info(
        'Removing member',
        extra={'team_id': pk, 'target_user_id': user_id, 'user_id': request.auth.id},
    )

    if team.captain_id == user_id:
        logger.warning('Member removal rejected, target is captain', extra={'team_id': pk})
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Captain cannot be removed from team.')

    assert_can_remove_member(team)

    removed_user = get_object_or_404(User, id=user_id)
    deleted_count, _ = TeamMember.objects.filter(team=team, user_id=user_id).delete()
    if deleted_count == 0:
        logger.warning(
            'Member removal rejected, not a member',
            extra={'team_id': pk, 'target_user_id': user_id},
        )
        raise_api_error(HTTPStatus.NOT_FOUND, 'User is not a team member.')

    member_removed.send(sender=remove_member_from_team, team=team, user=removed_user)

    clear_invitation_states_for_member(team=team, user_id=user_id)
    clear_join_request_states_for_member(team=team, user_id=user_id)
    logger.info(
        'Member removed',
        extra={'team_id': pk, 'target_user_id': user_id, 'user_id': request.auth.id},
    )
    return 204, None


@router.post(
    '/{int:pk}/leave',
    operation_id='leaveTeam',
    url_name='team_leave',
    response={200: DetailResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def leave_team(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    logger.info('Leave requested', extra={'team_id': pk, 'user_id': request.auth.id})

    if team.captain_id == request.auth.id:
        logger.warning(
            'Leave rejected, user is captain',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Captain cannot leave the team. Transfer captain role or delete the team.')

    assert_can_remove_member(team)

    deleted_count, _ = TeamMember.objects.filter(team=team, user=request.auth).delete()
    if deleted_count == 0:
        logger.warning(
            'Leave rejected, not a member',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'You are not a team member of this team.')

    member_left.send(sender=leave_team, team=team, user=request.auth)

    clear_invitation_states_for_member(team=team, user=request.auth)
    clear_join_request_states_for_member(team=team, user=request.auth)
    logger.info('User left team', extra={'team_id': pk, 'user_id': request.auth.id})
    return DetailResponse(
        detail='You left the team.'
    )


# --------------------------------------------------------------------------
# Invitations (inbox)
# --------------------------------------------------------------------------

@router.get(
    '/invitations',
    operation_id='listTeamInvitations',
    url_name='team_invitations',
    response={200: list[TeamInvitationInboxResponse], 401: ErrorResponse},
)
def list_team_invitations(request):
    logger.debug('Listing invitation inbox', extra={'user_id': request.auth.id})
    queryset = (
        TeamInvitation.objects.select_related('team', 'invited_by')
        .filter(user=request.auth)
        .exclude(team__team_members__user=request.auth)
        .order_by('-created_at')
    )
    ctx = {'request': request}
    return [TeamInvitationInboxResponse.model_validate(i, from_attributes=True, context=ctx) for i in queryset]


def respond_to_invitation(request, invitation_id: int, new_status: str):
    logger.info(
        'Responding to invitation',
        extra={
            'invitation_id': invitation_id,
            'user_id': request.auth.id,
            'new_status': new_status,
        },
    )

    with transaction.atomic():
        invitation = get_object_or_404(
            TeamInvitation.objects.select_for_update(of=('self',)).select_related('team__captain'),
            id=invitation_id,
            user=request.auth,
        )

        if invitation.status != TeamInvitation.STATUS_INVITED:
            logger.warning(
                'Invitation response rejected, already processed',
                extra={'invitation_id': invitation_id, 'status': invitation.status},
            )
            raise_api_error(HTTPStatus.BAD_REQUEST, 'This invitation is already processed.')

        now = timezone.now()

        if new_status == TeamInvitation.STATUS_ACCEPTED:
            assert_team_not_in_active_tournament(invitation.team)
            TeamMember.objects.get_or_create(team=invitation.team, user=request.auth)
            TeamJoinRequest.objects.filter(
                team=invitation.team,
                user=request.auth,
                status=TeamJoinRequest.STATUS_PENDING,
            ).update(
                status=TeamJoinRequest.STATUS_DECLINED,
                reviewed_by=invitation.team.captain,
                reviewed_at=now,
            )
            # Drop any stale duplicates but keep this one so it stays persisted
            # with its accepted status (signal receivers get a saved instance).
            TeamInvitation.objects.filter(
                team=invitation.team, user=request.auth,
            ).exclude(pk=invitation.pk).delete()

        invitation.status = new_status
        invitation.responded_at = now
        invitation.save(update_fields=['status', 'responded_at', 'updated_at'])

    invitation_responded.send(sender=respond_to_invitation, invitation=invitation)

    logger.info(
        'Invitation responded',
        extra={
            'status': new_status,
            'invitation_id': invitation_id,
            'team_id': invitation.team_id,
            'user_id': request.auth.id,
        },
    )

    team = get_object_or_404(get_team_queryset(), pk=invitation.team_id)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.post(
    '/invitations/{int:invitation_id}/accept',
    operation_id='acceptTeamInvitation',
    url_name='team_invitation_accept',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def accept_team_invitation(request, invitation_id: int):
    return respond_to_invitation(request, invitation_id, TeamInvitation.STATUS_ACCEPTED)


@router.post(
    '/invitations/{int:invitation_id}/decline',
    operation_id='declineTeamInvitation',
    url_name='team_invitation_decline',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def decline_team_invitation(request, invitation_id: int):
    return respond_to_invitation(request, invitation_id, TeamInvitation.STATUS_DECLINED)


# --------------------------------------------------------------------------
# Join requests
# --------------------------------------------------------------------------

@router.post(
    '/{int:pk}/join-requests',
    operation_id='createTeamJoinRequest',
    url_name='team_join_request_create',
    response={200: DetailResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def create_team_join_request(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    logger.info('Join request requested', extra={'team_id': pk, 'user_id': request.auth.id})
    assert_team_not_in_active_tournament(team)

    if not team.is_public:
        logger.warning(
            'Join request rejected, private team',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'Join requests are available only for public teams.')

    if is_team_member(team, request.auth):
        logger.warning(
            'Join request rejected, already a member',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'You are already in this team.')

    if TeamInvitation.objects.filter(
        team=team,
        user=request.auth,
        status=TeamInvitation.STATUS_INVITED,
    ).exists():
        logger.warning(
            'Join request rejected, pending invitation exists',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'You already have an invitation to this team.')

    if TeamJoinRequest.objects.filter(
        team=team,
        user=request.auth,
        status=TeamJoinRequest.STATUS_PENDING,
    ).exists():
        logger.warning(
            'Join request rejected, already pending',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.BAD_REQUEST, 'You already have a pending join request for this team.')

    join_request = TeamJoinRequest.objects.create(
        team=team,
        user=request.auth,
        status=TeamJoinRequest.STATUS_PENDING,
    )
    logger.info(
        'Join request created',
        extra={
            'join_request_id': join_request.id,
            'team_id': pk,
            'user_id': request.auth.id,
        },
    )

    join_request_received.send(sender=create_team_join_request, join_request=join_request)

    return 200, DetailResponse(detail='Join request sent.')


def review_join_request(request, pk: int, request_id: int, new_status: str):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id:
        logger.warning(
            'Join request review rejected, not captain',
            extra={'team_id': pk, 'join_request_id': request_id, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only captain can review join requests.')

    logger.info(
        'Reviewing join request',
        extra={
            'team_id': pk,
            'join_request_id': request_id,
            'new_status': new_status,
            'user_id': request.auth.id,
        },
    )

    with transaction.atomic():
        join_request = get_object_or_404(
            TeamJoinRequest.objects.select_for_update(of=('self',)).select_related('user'),
            id=request_id,
            team=team,
        )
        if join_request.status != TeamJoinRequest.STATUS_PENDING:
            logger.warning(
                'Join request review rejected, already processed',
                extra={'join_request_id': request_id, 'status': join_request.status},
            )
            raise_api_error(HTTPStatus.BAD_REQUEST, 'This join request is already processed.')

        if new_status == TeamJoinRequest.STATUS_ACCEPTED:
            assert_team_not_in_active_tournament(team)

        join_request.status = new_status
        join_request.reviewed_by = request.auth
        join_request.reviewed_at = timezone.now()
        join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

        if new_status == TeamJoinRequest.STATUS_ACCEPTED:
            TeamMember.objects.get_or_create(team=team, user=join_request.user)
            clear_invitation_states_for_member(team=team, user=join_request.user)

    logger.info(
        'Join request reviewed',
        extra={
            'status': new_status,
            'join_request_id': request_id,
            'team_id': pk,
            'applicant_id': join_request.user_id,
            'user_id': request.auth.id,
        },
    )

    join_request_responded.send(sender=review_join_request, join_request=join_request)

    team = get_object_or_404(get_team_queryset(), pk=pk)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.post(
    '/{int:pk}/join-requests/{int:request_id}/accept',
    operation_id='acceptTeamJoinRequest',
    url_name='team_join_request_accept',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def accept_team_join_request(request, pk: int, request_id: int):
    return review_join_request(request, pk, request_id, TeamJoinRequest.STATUS_ACCEPTED)


@router.post(
    '/{int:pk}/join-requests/{int:request_id}/decline',
    operation_id='declineTeamJoinRequest',
    url_name='team_join_request_decline',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def decline_team_join_request(request, pk: int, request_id: int):
    return review_join_request(request, pk, request_id, TeamJoinRequest.STATUS_DECLINED)


# --------------------------------------------------------------------------
# Per-team lists (captain / admin)
# --------------------------------------------------------------------------

@router.get(
    '/{int:pk}/invitations',
    operation_id='listTeamInvitationsByTeam',
    url_name='team_invitations_by_team',
    response={200: list[TeamInvitationResponse], 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def list_team_invitations_by_team(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id and not is_platform_admin(request.auth):
        logger.warning(
            'Invitation list rejected',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only captain or admin can view team invitations.')

    logger.debug(
        'Listing team invitations',
        extra={'team_id': pk, 'user_id': request.auth.id},
    )
    member_ids = {member.id for member in team.members.all()}
    member_ids.add(team.captain_id)

    queryset = (
        TeamInvitation.objects.filter(team=team)
        .exclude(user_id__in=member_ids)
        .select_related('user', 'invited_by')
        .order_by('-created_at')
    )
    ctx = {'request': request}
    return [TeamInvitationResponse.model_validate(i, from_attributes=True, context=ctx) for i in queryset]


@router.get(
    '/{int:pk}/join-requests',
    operation_id='listTeamJoinRequestsByTeam',
    url_name='team_join_request_list',
    response={200: list[TeamJoinRequestResponse], 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def list_team_join_requests_by_team(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id and not is_platform_admin(request.auth):
        logger.warning(
            'Join request list rejected',
            extra={'team_id': pk, 'user_id': request.auth.id},
        )
        raise_api_error(HTTPStatus.FORBIDDEN, 'Only captain or admin can view team join requests.')

    logger.debug(
        'Listing team join requests',
        extra={'team_id': pk, 'user_id': request.auth.id},
    )
    queryset = (
        TeamJoinRequest.objects.filter(team=team)
        .select_related('user', 'reviewed_by')
        .order_by('-created_at')
    )
    return queryset