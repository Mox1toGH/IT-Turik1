from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.db.models import Q

from accounts.utils.permissions import is_platform_admin
from teams.models import Team, TeamMember


class IsPlatformAdminPermission(BasePermission):
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return is_platform_admin(request.user)


class IsPlatformAdminOrReadOnly(BasePermission):
    message = 'Admin access required.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return is_platform_admin(request.user)


class IsTeamMemberPermission(BasePermission):
    message = 'Team membership is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and TeamMember.objects.filter(user=user).exists())


class IsPlatformAdminOrTeamMemberPermission(BasePermission):
    message = 'Admin or team membership is required.'

    def _extract_team_id(self, request, view):
        for key in ('team_id', 'team', 'team_pk'):
            value = view.kwargs.get(key)
            if value:
                return value

        for key in ('team_id', 'team'):
            value = request.query_params.get(key)
            if value:
                return value

        data = getattr(request, 'data', None) or {}
        for key in ('team_id', 'team'):
            value = data.get(key)
            if value:
                return value
        return None

    def _is_team_captain_or_member(self, user, team_id):
        team = Team.objects.filter(pk=team_id).only('id', 'captain_id').first()
        if not team:
            return False

        if team.captain_id == user.id:
            return True

        return TeamMember.objects.filter(team_id=team.id, user_id=user.id).exists()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_platform_admin(user):
            return True

        team_id = self._extract_team_id(request, view)
        if team_id is not None:
            return self._is_team_captain_or_member(user, team_id)

        return Team.objects.filter(
            Q(captain_id=user.id) | Q(team_members__user_id=user.id)
        ).exists()


class IsJuryPermission(BasePermission):
    message = 'Jury access required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == 'jury')


class IsOrganizerOrAdminPermission(BasePermission):
    message = 'Organizer or admin access required.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in ('organizer', 'admin') or user.is_superuser
