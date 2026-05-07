import re

from django.utils import timezone
from rest_framework import serializers

from backend.permissions import is_platform_admin
from accounts.models import User

from .models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from .services import assert_team_not_in_active_tournament, get_active_tournament_registration


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


def get_user_invitation_status(*, team, user):
    """Get the invitation status for a user in a specific team. Returns None if not invited or already a member."""
    if not user:
        return None
    
    is_member = any(member.id == user.id for member in team.members.all())
    is_captain = team.captain_id == user.id
    if is_member or is_captain:
        return None

    for invitation in team.invitations.all():
        if invitation.user_id == user.id:
            return invitation.status
    return None


def get_user_join_request_status(*, team, user):
    """Get the join request status for a user in a specific team. Returns None if no pending request."""
    if not user:
        return None

    for join_request in team.join_requests.all():
        if join_request.user_id == user.id:
            return join_request.status
    return None


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role')


class TeamSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'is_public')


class TeamInvitationSerializer(serializers.ModelSerializer):
    user = TeamMemberSerializer(read_only=True)
    invited_by_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = TeamInvitation
        fields = ('id', 'user', 'status', 'created_at', 'responded_at', 'invited_by_id')


class TeamJoinRequestSerializer(serializers.ModelSerializer):
    user = TeamMemberSerializer(read_only=True)
    reviewed_by_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = TeamJoinRequest
        fields = ('id', 'user', 'status', 'created_at', 'reviewed_at', 'reviewed_by_id')


class TeamInvitationInboxSerializer(serializers.ModelSerializer):
    team = TeamSummarySerializer(read_only=True)
    invited_by = TeamMemberSerializer(read_only=True)

    class Meta:
        model = TeamInvitation
        fields = ('id', 'team', 'status', 'created_at', 'responded_at', 'invited_by')


class TeamSerializer(serializers.ModelSerializer):
    captain_id = serializers.IntegerField(source='captain.id', read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=False,
    )
    members = TeamMemberSerializer(many=True, read_only=True)
    is_member = serializers.SerializerMethodField()
    is_captain = serializers.SerializerMethodField()
    can_request_to_join = serializers.SerializerMethodField()
    is_in_active_tournament = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            'id',
            'name',
            'email',
            'captain_id',
            'is_public',
            'organization',
            'contact_telegram',
            'contact_discord',
            'members',
            'is_member',
            'is_captain',
            'can_request_to_join',
            'is_in_active_tournament',
            'member_ids',
        )

    def _request_user(self):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        return request.user

    def _is_member_for_user(self, obj, user):
        if not user:
            return False
        return any(member.id == user.id for member in obj.members.all())

    def get_is_member(self, obj):
        user = self._request_user()
        if not user:
            return False
        return self._is_member_for_user(obj, user)

    def get_is_captain(self, obj):
        user = self._request_user()
        return bool(user) and obj.captain_id == user.id

    def get_can_request_to_join(self, obj):
        user = self._request_user()
        if not user or not obj.is_public:
            return False
        if self._is_member_for_user(obj, user) or obj.captain_id == user.id:
            return False
        
        invitation_status = get_user_invitation_status(team=obj, user=user)
        if invitation_status == TeamInvitation.STATUS_INVITED:
            return False
        
        join_request_status = get_user_join_request_status(team=obj, user=user)
        return join_request_status != TeamJoinRequest.STATUS_PENDING

    def get_is_in_active_tournament(self, obj):
        return get_active_tournament_registration(obj) is not None

    def validate_contact_telegram(self, value):
        normalized = value.strip().lstrip('@')
        if not normalized:
            return ''

        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{4,31}', normalized):
            raise serializers.ValidationError(
                'Telegram username must be 5-32 chars, start with a letter, and contain only letters, digits, or _.'
            )

        return normalized

    def validate_contact_discord(self, value):
        normalized = value.strip().lstrip('@')
        if not normalized:
            return ''

        if not re.fullmatch(r'(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?', normalized):
            raise serializers.ValidationError(
                'Discord username must be 2-32 chars and may contain letters, digits, ".", "_" and optional #1234.'
            )

        return normalized

    def validate_member_ids(self, value):
        if not value:
            return []

        unique_ids = sorted(set(value))
        existing_ids = set(User.objects.filter(id__in=unique_ids).values_list('id', flat=True))
        missing_ids = [user_id for user_id in unique_ids if user_id not in existing_ids]
        if missing_ids:
            raise serializers.ValidationError(
                {'member_ids': [f'Users not found: {missing_ids}']}
            )
        return unique_ids

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        captain = validated_data.pop('captain')

        team = Team.objects.create(captain=captain, **validated_data)
        TeamMember.objects.get_or_create(team=team, user=captain)

        invited_users = User.objects.filter(id__in=member_ids).exclude(id=captain.id)
        for user in invited_users:
            invite_user_to_team(team=team, user=user, invited_by=captain)

        return team

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        instance = super().update(instance, validated_data)

        if member_ids is not None:
            request_user = self._request_user() or instance.captain
            invited_users = User.objects.filter(id__in=member_ids).exclude(id=instance.captain_id)
            for user in invited_users:
                invite_user_to_team(team=instance, user=user, invited_by=request_user)

        return instance
