import re

from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

from backend.permissions import is_platform_admin
from backend.openapi import _400, _401, _403, _404
from accounts.models import User

from .models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from .serializers import (
    clear_invitation_states_for_member,
    clear_join_request_states_for_member,
    TeamDetailResponseSerializer,
    TeamInvitationInboxSerializer,
    TeamInvitationSerializer,
    TeamJoinRequestSerializer,
    TeamBannerSerializer,
    TeamSerializer,
    invite_user_to_team,
)
from .services import assert_can_remove_member, assert_team_not_in_active_tournament
from .permissions import CanCreateTeam, IsNotPlatformAdminOrReadOnly
from .signals import (
    invitation_received,
    invitation_responded,
    join_request_received,
    join_request_responded,
    member_removed,
    member_left,
)


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


@extend_schema(methods=['GET'], operation_id='listTeams', responses={
    200: TeamSerializer(many=True),
    401: _401,
})
@extend_schema(methods=['POST'], operation_id='createTeam', responses={
    201: TeamSerializer,
    400: _400,
    401: _401,
    403: _403,
})
class TeamListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            permission_classes.append(CanCreateTeam)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if is_platform_admin(self.request.user):
            return get_team_queryset()

        user_id = self.request.user.id
        return (
            get_team_queryset()
            .filter(
                Q(is_public=True)
                | Q(captain_id=user_id)
                | Q(team_members__user_id=user_id)
            )
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(captain=self.request.user)


@extend_schema(methods=['GET'], operation_id='getTeam', responses={
    200: TeamSerializer,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceTeam', responses={
    200: TeamSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateTeam', responses={
    200: TeamSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteTeam', responses={
    204: OpenApiResponse(description='Team deleted successfully.'),
    401: _401,
    403: _403,
    404: _404,
})
class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsNotPlatformAdminOrReadOnly]
    serializer_class = TeamSerializer

    def get_queryset(self):
        return get_team_queryset()

    def get_object(self):
        team = super().get_object()
        if team.is_public or is_team_member(team, self.request.user) or is_platform_admin(self.request.user):
            return team
        raise PermissionDenied('You do not have access to this private team.')

    def _assert_captain(self, team):
        if team.captain_id != self.request.user.id:
            raise PermissionDenied('Only captain can modify this team.')
        return None

    @staticmethod
    def _is_team_identity_mutation(request_data):
        return 'name' in request_data or 'is_public' in request_data

    def update(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        if self._is_team_identity_mutation(request.data):
            assert_team_not_in_active_tournament(team)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        if self._is_team_identity_mutation(request.data):
            assert_team_not_in_active_tournament(team)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().destroy(request, *args, **kwargs)

@extend_schema(methods=['PUT', 'PATCH'], operation_id='updateTeamBanner', request={
    'multipart/form-data': {
        'type': 'object',
        'properties': {
            'banner': {
                'type': 'string',
                'format': 'binary',
            }
        }
    }
}, responses={
    200: TeamBannerSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteTeamBanner', responses={
    200: TeamBannerSerializer,
    401: _401,
    403: _403,
    404: _404,
})
class TeamBannerView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsNotPlatformAdminOrReadOnly]
    serializer_class = TeamBannerSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return get_team_queryset()

    def get_object(self):
        team = super().get_object()
        if team.is_public or is_team_member(team, self.request.user) or is_platform_admin(self.request.user):
            return team
        raise PermissionDenied('You do not have access to this private team.')

    def _assert_captain(self, team):
        if team.captain_id != self.request.user.id:
            raise PermissionDenied('Only captain can modify this team banner.')
        return None

    def patch(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        if team.banner:
            team.banner.delete(save=False)
            team.banner = None
            team.save(update_fields=['banner'])
        serializer = TeamSerializer(team, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='inviteMemberToTeam',
    request=inline_serializer("InviteMemberRequest", fields={"user_id": drf_serializers.IntegerField()}),
    responses={
        200: TeamSerializer,
        201: TeamSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TeamMemberInviteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            raise PermissionDenied('Only captain can manage members.')

        assert_team_not_in_active_tournament(team)

        user_id = request.data.get('user_id')
        if not user_id:
            raise ValidationError({'user_id': ['user_id is required.']})

        user = get_object_or_404(User, id=user_id)
        if user.id == team.captain_id:
            raise ValidationError({'message': ['Captain is already on the team.']})

        if TeamMember.objects.filter(team=team, user=user).exists():
            raise ValidationError({'message': ['User is already a team member.']})

        invitation, created = invite_user_to_team(team=team, user=user, invited_by=request.user)
        if not invitation:
            raise ValidationError({'message': ['Unable to invite this user.']})

        invitation_received.send(sender=self.__class__, invitation=invitation)

        team.refresh_from_db()
        return Response(
            TeamSerializer(team, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='removeMemberFromTeam',
    responses={
        204: OpenApiResponse(description='Member removed successfully.'),
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TeamMemberRemoveView(generics.GenericAPIView):
    serializer_class = TeamSerializer

    def delete(self, request, pk, user_id):
        team = get_object_or_404(get_team_queryset(), pk=pk)
        if team.captain_id != request.user.id:
            raise PermissionDenied('Only captain can manage members.')

        if team.captain_id == user_id:
            raise ValidationError({'message': ['Captain cannot be removed from team.']})

        assert_can_remove_member(team)

        removed_user = get_object_or_404(User, id=user_id)
        deleted_count, _ = TeamMember.objects.filter(team=team, user_id=user_id).delete()
        if deleted_count == 0:
            raise NotFound('User is not a team member.')

        member_removed.send(sender=self.__class__, team=team, user=removed_user)

        clear_invitation_states_for_member(team=team, user_id=user_id)
        clear_join_request_states_for_member(team=team, user_id=user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    operation_id='leaveTeam',
    request=None,
    responses={
        200: TeamDetailResponseSerializer,
        400: _400,
        401: _401,
        404: _404,
    },
)
class TeamLeaveView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamDetailResponseSerializer

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)

        if team.captain_id == request.user.id:
            raise ValidationError(
                {'message': ['Captain cannot leave the team. Transfer captain role or delete the team.']}
            )

        deleted_count, _ = TeamMember.objects.filter(team=team, user=request.user).delete()
        if deleted_count == 0:
            raise ValidationError({'message': ['You are not a team member of this team.']})

        member_left.send(sender=self.__class__, team=team, user=request.user)

        clear_invitation_states_for_member(team=team, user=request.user)
        clear_join_request_states_for_member(team=team, user=request.user)
        return Response(
            TeamDetailResponseSerializer({'detail': 'You left the team.'}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='listTeamInvitations',
    responses={
        200: TeamInvitationInboxSerializer(many=True),
        401: _401,
    },
)
class TeamInvitationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamInvitationInboxSerializer

    def get_queryset(self):
        return (
            TeamInvitation.objects.select_related('team', 'invited_by')
            .filter(user=self.request.user)
            .exclude(team__team_members__user=self.request.user)
            .order_by('-created_at')
        )


class TeamInvitationRespondView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    new_status = None

    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            TeamInvitation.objects.select_related('team'),
            id=invitation_id,
            user=request.user,
        )

        if invitation.status != TeamInvitation.STATUS_INVITED:
            raise ValidationError({'message': ['This invitation is already processed.']})

        now = timezone.now()

        if self.new_status == TeamInvitation.STATUS_ACCEPTED:
            assert_team_not_in_active_tournament(invitation.team)
            TeamMember.objects.get_or_create(team=invitation.team, user=request.user)
            TeamJoinRequest.objects.filter(
                team=invitation.team,
                user=request.user,
                status=TeamJoinRequest.STATUS_PENDING,
            ).update(
                status=TeamJoinRequest.STATUS_DECLINED,
                reviewed_by=invitation.team.captain,
                reviewed_at=now,
            )
            invitation.status = TeamInvitation.STATUS_ACCEPTED
            invitation.responded_at = now
            clear_invitation_states_for_member(team=invitation.team, user=request.user)
            invitation_responded.send(sender=self.__class__, invitation=invitation)
        else:
            invitation.status = self.new_status
            invitation.responded_at = now
            invitation.save(update_fields=['status', 'responded_at', 'updated_at'])
            invitation_responded.send(sender=self.__class__, invitation=invitation)

        team = get_object_or_404(get_team_queryset(), pk=invitation.team_id)
        return Response(
            TeamSerializer(team, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='acceptTeamInvitation',
    request=None,
    responses={
        200: TeamSerializer,
        400: _400,
        401: _401,
        404: _404,
    },
)
class TeamInvitationAcceptView(TeamInvitationRespondView):
    new_status = TeamInvitation.STATUS_ACCEPTED


@extend_schema(
    operation_id='declineTeamInvitation',
    request=None,
    responses={
        200: TeamSerializer,
        400: _400,
        401: _401,
        404: _404,
    },
)
class TeamInvitationDeclineView(TeamInvitationRespondView):
    new_status = TeamInvitation.STATUS_DECLINED


@extend_schema(
    operation_id='createTeamJoinRequest',
    responses={
        200: TeamDetailResponseSerializer,
        201: TeamDetailResponseSerializer,
        400: _400,
        401: _401,
        404: _404,
    },
)
class TeamJoinRequestCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamDetailResponseSerializer

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)
        assert_team_not_in_active_tournament(team)

        if not team.is_public:
            raise ValidationError({'message': ['Join requests are available only for public teams.']})

        if is_team_member(team, request.user):
            raise ValidationError({'message': ['You are already in this team.']})

        if TeamInvitation.objects.filter(
            team=team,
            user=request.user,
            status=TeamInvitation.STATUS_INVITED,
        ).exists():
            raise ValidationError({'message': ['You already have an invitation to this team.']})

        join_request, created = TeamJoinRequest.objects.get_or_create(
            team=team,
            user=request.user,
            defaults={'status': TeamJoinRequest.STATUS_PENDING},
        )

        if not created:
            if join_request.status == TeamJoinRequest.STATUS_PENDING:
                return Response(
                    TeamDetailResponseSerializer({'detail': 'Join request already sent.'}).data,
                    status=status.HTTP_200_OK,
                )
            join_request.status = TeamJoinRequest.STATUS_PENDING
            join_request.reviewed_by = None
            join_request.reviewed_at = None
            join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

        join_request_received.send(sender=self.__class__, join_request=join_request)

        return Response(
            TeamDetailResponseSerializer({'detail': 'Join request sent.'}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TeamJoinRequestReviewView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    new_status = None

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk, request_id):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            raise PermissionDenied('Only captain can review join requests.')

        join_request = get_object_or_404(TeamJoinRequest, id=request_id, team=team)
        if join_request.status != TeamJoinRequest.STATUS_PENDING:
            raise ValidationError({'message': ['This join request is already processed.']})

        if self.new_status == TeamJoinRequest.STATUS_ACCEPTED:
            assert_team_not_in_active_tournament(team)

        now = timezone.now()
        join_request.status = self.new_status
        join_request.reviewed_by = request.user
        join_request.reviewed_at = now
        join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

        if self.new_status == TeamJoinRequest.STATUS_ACCEPTED:
            TeamMember.objects.get_or_create(team=team, user=join_request.user)
            clear_invitation_states_for_member(team=team, user=join_request.user)

        join_request_responded.send(sender=self.__class__, join_request=join_request)

        team.refresh_from_db()
        return Response(
            TeamSerializer(team, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='acceptTeamJoinRequest',
    request=None,
    responses={
        200: TeamSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TeamJoinRequestAcceptView(TeamJoinRequestReviewView):
    new_status = TeamJoinRequest.STATUS_ACCEPTED


@extend_schema(
    operation_id='declineTeamJoinRequest',
    request=None,
    responses={
        200: TeamSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TeamJoinRequestDeclineView(TeamJoinRequestReviewView):
    new_status = TeamJoinRequest.STATUS_DECLINED


@extend_schema(
    operation_id='listTeamInvitationsByTeam',
    responses={
        200: TeamInvitationSerializer(many=True),
        401: _401,
        403: _403,
        404: _404,
    },
)
class TeamInvitationListByTeamView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamInvitationSerializer

    def get_queryset(self):
        team_id = self.kwargs.get('pk')
        team = get_object_or_404(get_team_queryset(), pk=team_id)

        if team.captain_id != self.request.user.id and not is_platform_admin(self.request.user):
            raise PermissionDenied('Only captain or admin can view team invitations.')

        member_ids = {member.id for member in team.members.all()}
        member_ids.add(team.captain_id)

        return (
            TeamInvitation.objects
            .filter(team=team)
            .exclude(user_id__in=member_ids)
            .select_related('user', 'invited_by')
            .order_by('-created_at')
        )


@extend_schema(
    operation_id='listTeamJoinRequestsByTeam',
    responses={
        200: TeamJoinRequestSerializer(many=True),
        401: _401,
        403: _403,
        404: _404,
    },
)
class TeamJoinRequestListByTeamView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamJoinRequestSerializer

    def get_queryset(self):
        team_id = self.kwargs.get('pk')
        team = get_object_or_404(get_team_queryset(), pk=team_id)

        if team.captain_id != self.request.user.id and not is_platform_admin(self.request.user):
            raise PermissionDenied('Only captain or admin can view team join requests.')

        return (
            TeamJoinRequest.objects
            .filter(team=team)
            .select_related('user', 'reviewed_by')
            .order_by('-created_at')
        )