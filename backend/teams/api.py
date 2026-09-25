import re

from django.db import transaction
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import File, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile

from accounts.models import User
from backend.auth import JWTAuth
from backend.permissions import is_platform_admin

from .models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from backend.schemas import ErrorResponse
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
    raise HttpError(403, 'You do not have access to this private team.')


def deny_platform_admin_write(request):
    # Replaces IsNotPlatformAdminOrReadOnly for non-safe methods.
    if is_platform_admin(request.auth):
        raise HttpError(403, 'Platform administrators have read-only access.')


def assert_can_create_team(user):
    # Replaces CanCreateTeam. TODO: put your original permission logic here.
    if is_platform_admin(user) or user.role != 'team':
        raise HttpError(403, 'You do not have permission to create a team.')


def normalize_telegram(value: str) -> str:
    normalized = value.strip().lstrip('@')
    if not normalized:
        return ''
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{4,31}', normalized):
        raise HttpError(
            400,
            'Telegram username must be 5-32 chars, start with a letter, and contain only letters, digits, or _.',
        )
    return normalized


def normalize_discord(value: str) -> str:
    normalized = value.strip().lstrip('@')
    if not normalized:
        return ''
    if not re.fullmatch(r'(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?', normalized):
        raise HttpError(
            400,
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
        raise HttpError(400, f'Users not found: {missing_ids}')
    return unique_ids


def clear_invitation_states_for_member(*, team, user=None, user_id=None):
    target_user_id = user_id or getattr(user, 'id', None)
    if not target_user_id:
        return
    TeamInvitation.objects.filter(team=team, user_id=target_user_id).delete()


def clear_join_request_states_for_member(*, team, user=None, user_id=None):
    target_user_id = user_id or getattr(user, 'id', None)
    if not target_user_id:
        return
    TeamJoinRequest.objects.filter(team=team, user_id=target_user_id).delete()


def invite_user_to_team(*, team, user, invited_by):
    assert_team_not_in_active_tournament(team)

    if TeamMember.objects.filter(team=team, user=user).exists():
        return None, False

    invitation, created = TeamInvitation.objects.get_or_create(
        team=team,
        user=user,
        defaults={
            'invited_by': invited_by,
            'status': TeamInvitation.STATUS_INVITED,
        },
    )

    if not created:
        invitation.status = TeamInvitation.STATUS_INVITED
        invitation.responded_at = None
        invitation.invited_by = invited_by
        invitation.save(update_fields=['status', 'responded_at', 'invited_by', 'updated_at'])

    TeamJoinRequest.objects.filter(
        team=team,
        user=user,
        status=TeamJoinRequest.STATUS_PENDING,
    ).update(
        status=TeamJoinRequest.STATUS_DECLINED,
        reviewed_by=invited_by,
        reviewed_at=timezone.now(),
    )

    return invitation, created


# --------------------------------------------------------------------------
# Teams
# --------------------------------------------------------------------------

@router.get(
    '/',
    operation_id='listTeams',
    response={200: list[TeamResponse], 401: ErrorResponse},
)
def list_teams(request):
    user = request.auth
    queryset = get_team_queryset()
    if not is_platform_admin(user):
        queryset = queryset.filter(
            Q(is_public=True) | Q(captain_id=user.id) | Q(team_members__user_id=user.id)
        ).distinct()

    return list(queryset.iterator(chunk_size=100))


@router.post(
    '/',
    operation_id='createTeam',
    response={201: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse},
)
def create_team(request, payload: TeamCreateRequest):
    user = request.auth
    assert_can_create_team(user)

    contact_telegram = normalize_telegram(payload.contact_telegram)
    contact_discord = normalize_discord(payload.contact_discord)
    member_ids = validate_member_ids(payload.member_ids)

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
            invite_user_to_team(team=team, user=invited_user, invited_by=user)

    team = get_object_or_404(get_team_queryset(), pk=team.pk)
    return 201, TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.get(
    '/{int:pk}',
    operation_id='getTeam',
    response={200: TeamResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def get_team(request, pk: int):
    team = get_accessible_team(request, pk)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


def apply_team_update(request, pk: int, payload: TeamUpdateRequest):
    deny_platform_admin_write(request)
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        raise HttpError(403, 'Only captain can modify this team.')

    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    member_ids = data.pop('member_ids', None)

    if 'name' in data or 'is_public' in data:
        assert_team_not_in_active_tournament(team)

    if 'contact_telegram' in data:
        data['contact_telegram'] = normalize_telegram(data['contact_telegram'])
    if 'contact_discord' in data:
        data['contact_discord'] = normalize_discord(data['contact_discord'])
    if member_ids is not None:
        member_ids = validate_member_ids(member_ids)

    with transaction.atomic():
        for field, value in data.items():
            setattr(team, field, value)
        team.save()

        if member_ids is not None:
            for invited_user in User.objects.filter(id__in=member_ids).exclude(id=team.captain_id):
                invite_user_to_team(team=team, user=invited_user, invited_by=request.auth)

    team = get_object_or_404(get_team_queryset(), pk=team.pk)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.put(
    '/{int:pk}',
    operation_id='replaceTeam',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def replace_team(request, pk: int, payload: TeamUpdateRequest):
    return apply_team_update(request, pk, payload)


@router.patch(
    '/{int:pk}',
    operation_id='updateTeam',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def update_team(request, pk: int, payload: TeamUpdateRequest):
    return apply_team_update(request, pk, payload)


@router.delete(
    '/{int:pk}',
    operation_id='deleteTeam',
    response={204: None, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def delete_team(request, pk: int):
    deny_platform_admin_write(request)
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        raise HttpError(403, 'Only captain can modify this team.')
    team.delete()
    return 204, None


# --------------------------------------------------------------------------
# Banner
# --------------------------------------------------------------------------

def apply_banner_upload(request, pk: int, banner: UploadedFile):
    deny_platform_admin_write(request)
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        raise HttpError(403, 'Only captain can modify this team banner.')
    if not (banner.content_type or '').startswith('image/'):
        raise HttpError(400, 'Upload a valid image.')

    team.banner = banner
    team.save(update_fields=['banner'])
    team.refresh_from_db()
    return TeamBannerResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.put(
    '/{int:pk}/banner',
    operation_id='teamBannerUpdate',
    response={200: TeamBannerResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def replace_team_banner(request, pk: int, banner: UploadedFile = File(...)):
    return apply_banner_upload(request, pk, banner)


@router.patch(
    '/{int:pk}/banner',
    operation_id='teamBannerPartialUpdate',
    response={200: TeamBannerResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def update_team_banner(request, pk: int, banner: UploadedFile = File(...)):
    return apply_banner_upload(request, pk, banner)


@router.delete(
    '/{int:pk}/banner',
    operation_id='deleteTeamBanner',
    response={200: TeamResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def delete_team_banner(request, pk: int):
    deny_platform_admin_write(request)
    team = get_accessible_team(request, pk)
    if team.captain_id != request.auth.id:
        raise HttpError(403, 'Only captain can modify this team banner.')

    if team.banner:
        team.banner.delete(save=False)
        team.banner = None
        team.save(update_fields=['banner'])
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


# --------------------------------------------------------------------------
# Members
# --------------------------------------------------------------------------

@router.post(
    '/{int:pk}/members/invite',
    operation_id='inviteMemberToTeam',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def invite_member_to_team(request, pk: int, payload: InviteMemberRequest):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id:
        raise HttpError(403, 'Only captain can manage members.')

    assert_team_not_in_active_tournament(team)

    if not payload.user_id:
        raise HttpError(400, 'user_id is required.')

    user = get_object_or_404(User, id=payload.user_id)
    if user.id == team.captain_id:
        raise HttpError(400, 'Captain is already on the team.')

    if TeamMember.objects.filter(team=team, user=user).exists():
        raise HttpError(400, 'User is already a team member.')

    invitation, created = invite_user_to_team(team=team, user=user, invited_by=request.auth)
    if not invitation:
        raise HttpError(400, 'Unable to invite this user.')

    invitation_received.send(sender=invite_member_to_team, invitation=invitation)

    team = get_object_or_404(get_team_queryset(), pk=pk)
    return TeamResponse.model_validate(
        team, from_attributes=True, context={'request': request}
    )


@router.delete(
    '/{int:pk}/members/{int:user_id}',
    operation_id='removeMemberFromTeam',
    response={204: None, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def remove_member_from_team(request, pk: int, user_id: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id:
        raise HttpError(403, 'Only captain can manage members.')

    if team.captain_id == user_id:
        raise HttpError(400, 'Captain cannot be removed from team.')

    assert_can_remove_member(team)

    removed_user = get_object_or_404(User, id=user_id)
    deleted_count, _ = TeamMember.objects.filter(team=team, user_id=user_id).delete()
    if deleted_count == 0:
        raise HttpError(404, 'User is not a team member.')

    member_removed.send(sender=remove_member_from_team, team=team, user=removed_user)

    clear_invitation_states_for_member(team=team, user_id=user_id)
    clear_join_request_states_for_member(team=team, user_id=user_id)
    return 204, None


@router.post(
    '/{int:pk}/leave',
    operation_id='leaveTeam',
    response={200: DetailResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def leave_team(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)

    if team.captain_id == request.auth.id:
        raise HttpError(400, 'Captain cannot leave the team. Transfer captain role or delete the team.')

    deleted_count, _ = TeamMember.objects.filter(team=team, user=request.auth).delete()
    if deleted_count == 0:
        raise HttpError(400, 'You are not a team member of this team.')

    member_left.send(sender=leave_team, team=team, user=request.auth)

    clear_invitation_states_for_member(team=team, user=request.auth)
    clear_join_request_states_for_member(team=team, user=request.auth)
    return DetailResponse(
        detail='You left the team.'
    )


# --------------------------------------------------------------------------
# Invitations (inbox)
# --------------------------------------------------------------------------

@router.get(
    '/invitations',
    operation_id='listTeamInvitations',
    response={200: list[TeamInvitationInboxResponse], 401: ErrorResponse},
)
def list_team_invitations(request):
    queryset = (
        TeamInvitation.objects.select_related('team', 'invited_by')
        .filter(user=request.auth)
        .exclude(team__team_members__user=request.auth)
        .order_by('-created_at')
    )
    ctx = {'request': request}
    return [TeamInvitationInboxResponse.model_validate(i, from_attributes=True, context=ctx) for i in queryset]


def respond_to_invitation(request, invitation_id: int, new_status: str):
    invitation = get_object_or_404(
        TeamInvitation.objects.select_related('team'),
        id=invitation_id,
        user=request.auth,
    )

    if invitation.status != TeamInvitation.STATUS_INVITED:
        raise HttpError(400, 'This invitation is already processed.')

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
        invitation.status = TeamInvitation.STATUS_ACCEPTED
        invitation.responded_at = now
        clear_invitation_states_for_member(team=invitation.team, user=request.auth)
        invitation_responded.send(sender=respond_to_invitation, invitation=invitation)
    else:
        invitation.status = new_status
        invitation.responded_at = now
        invitation.save(update_fields=['status', 'responded_at', 'updated_at'])
        invitation_responded.send(sender=respond_to_invitation, invitation=invitation)

    team = get_object_or_404(get_team_queryset(), pk=invitation.team_id)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.post(
    '/invitations/{int:invitation_id}/accept',
    operation_id='acceptTeamInvitation',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def accept_team_invitation(request, invitation_id: int):
    return respond_to_invitation(request, invitation_id, TeamInvitation.STATUS_ACCEPTED)


@router.post(
    '/invitations/{int:invitation_id}/decline',
    operation_id='declineTeamInvitation',
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
    response={200: DetailResponse, 201: DetailResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def create_team_join_request(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    assert_team_not_in_active_tournament(team)

    if not team.is_public:
        raise HttpError(400, 'Join requests are available only for public teams.')

    if is_team_member(team, request.auth):
        raise HttpError(400, 'You are already in this team.')

    if TeamInvitation.objects.filter(
        team=team,
        user=request.auth,
        status=TeamInvitation.STATUS_INVITED,
    ).exists():
        raise HttpError(400, 'You already have an invitation to this team.')

    join_request = TeamJoinRequest.objects.create(
        team=team,
        user=request.auth,
        defaults={'status': TeamJoinRequest.STATUS_PENDING},
    )

    join_request_received.send(sender=create_team_join_request, join_request=join_request)

    return DetailResponse(detail='Join request sent.')


def review_join_request(request, pk: int, request_id: int, new_status: str):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id:
        raise HttpError(403, 'Only captain can review join requests.')

    join_request = get_object_or_404(TeamJoinRequest, id=request_id, team=team)
    if join_request.status != TeamJoinRequest.STATUS_PENDING:
        raise HttpError(400, 'This join request is already processed.')

    if new_status == TeamJoinRequest.STATUS_ACCEPTED:
        assert_team_not_in_active_tournament(team)

    join_request.status = new_status
    join_request.reviewed_by = request.auth
    join_request.reviewed_at = timezone.now()
    join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

    if new_status == TeamJoinRequest.STATUS_ACCEPTED:
        TeamMember.objects.get_or_create(team=team, user=join_request.user)
        clear_invitation_states_for_member(team=team, user=join_request.user)

    join_request_responded.send(sender=review_join_request, join_request=join_request)

    team = get_object_or_404(get_team_queryset(), pk=pk)
    return TeamResponse.model_validate(team, from_attributes=True, context={'request': request})


@router.post(
    '/{int:pk}/join-requests/{int:request_id}/accept',
    operation_id='acceptTeamJoinRequest',
    response={200: TeamResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def accept_team_join_request(request, pk: int, request_id: int):
    return review_join_request(request, pk, request_id, TeamJoinRequest.STATUS_ACCEPTED)


@router.post(
    '/{int:pk}/join-requests/{int:request_id}/decline',
    operation_id='declineTeamJoinRequest',
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
    response={200: list[TeamInvitationResponse], 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def list_team_invitations_by_team(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id and not is_platform_admin(request.auth):
        raise HttpError(403, 'Only captain or admin can view team invitations.')

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
    response={200: list[TeamJoinRequestResponse], 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse},
)
def list_team_join_requests_by_team(request, pk: int):
    team = get_object_or_404(get_team_queryset(), pk=pk)
    if team.captain_id != request.auth.id and not is_platform_admin(request.auth):
        raise HttpError(403, 'Only captain or admin can view team join requests.')

    queryset = (
        TeamJoinRequest.objects.filter(team=team)
        .select_related('user', 'reviewed_by')
        .order_by('-created_at')
    )
    return queryset
