from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.permissions import is_platform_admin
from accounts.models import User

from .models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from .serializers import (
    clear_invitation_states_for_member,
    clear_join_request_states_for_member,
    TeamInvitationInboxSerializer,
    TeamInvitationSerializer,
    TeamJoinRequestSerializer,
    TeamMemberSerializer,
    TeamSerializer,
    invite_user_to_team,
)
from .services import assert_can_remove_member, assert_team_not_in_active_tournament
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


class TeamListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

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


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
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


class TeamMemberManageView(APIView):
    permission_classes = [IsAuthenticated]

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
        serializer = TeamSerializer(team, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, pk, user_id):
        team = self._get_team(pk)
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


class TeamLeaveView(APIView):
    permission_classes = [IsAuthenticated]

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
        return Response({'detail': 'You left the team.'}, status=status.HTTP_200_OK)


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


class TeamInvitationRespondView(APIView):
    permission_classes = [IsAuthenticated]
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
        serializer = TeamSerializer(team, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamInvitationAcceptView(TeamInvitationRespondView):
    new_status = TeamInvitation.STATUS_ACCEPTED


class TeamInvitationDeclineView(TeamInvitationRespondView):
    new_status = TeamInvitation.STATUS_DECLINED


class TeamJoinRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

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
                return Response({'detail': 'Join request already sent.'}, status=status.HTTP_200_OK)
            join_request.status = TeamJoinRequest.STATUS_PENDING
            join_request.reviewed_by = None
            join_request.reviewed_at = None
            join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

        join_request_received.send(sender=self.__class__, join_request=join_request)

        return Response({'detail': 'Join request sent.'}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class TeamJoinRequestReviewView(APIView):
    permission_classes = [IsAuthenticated]
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
        serializer = TeamSerializer(team, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamJoinRequestAcceptView(TeamJoinRequestReviewView):
    new_status = TeamJoinRequest.STATUS_ACCEPTED


class TeamJoinRequestDeclineView(TeamJoinRequestReviewView):
    new_status = TeamJoinRequest.STATUS_DECLINED


class TeamInvitationListByTeamView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamInvitationSerializer

    def get_queryset(self):
        team_id = self.kwargs.get('pk')
        team = get_object_or_404(get_team_queryset(), pk=team_id)
        
        # Only captain or admin can see invitations
        if team.captain_id != self.request.user.id and not is_platform_admin(self.request.user):
            raise PermissionDenied('Only captain or admin can view team invitations.')
        
        # Exclude invitations for users already in the team
        member_ids = {member.id for member in team.members.all()}
        member_ids.add(team.captain_id)
        
        return (
            TeamInvitation.objects
            .filter(team=team)
            .exclude(user_id__in=member_ids)
            .select_related('user', 'invited_by')
            .order_by('-created_at')
        )


class TeamJoinRequestListByTeamView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamJoinRequestSerializer

    def get_queryset(self):
        team_id = self.kwargs.get('pk')
        team = get_object_or_404(get_team_queryset(), pk=team_id)
        
        # Only captain or admin can see join requests
        if team.captain_id != self.request.user.id and not is_platform_admin(self.request.user):
            raise PermissionDenied('Only captain or admin can view team join requests.')
        
        return (
            TeamJoinRequest.objects
            .filter(team=team)
            .select_related('user', 'reviewed_by')
            .order_by('-created_at')
        )


