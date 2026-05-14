from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.db.models import Q

from backend.permissions import Permission, has_permission as user_has_permission, is_platform_admin
from teams.models import Team, TeamMember


class HasTournamentPermission(BasePermission):
    message = 'Tournament permission required.'
    required_permission = None

    def has_permission(self, request, view):
        return user_has_permission(request.user, self.required_permission)


class HasTournamentPermissionOrReadOnly(HasTournamentPermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class CanCreateTournament(HasTournamentPermission):
    required_permission = Permission.CREATE_TOURNAMENT


class CanEditTournament(HasTournamentPermission):
    required_permission = Permission.EDIT_TOURNAMENT


class CanDeleteTournament(HasTournamentPermission):
    required_permission = Permission.DELETE_TOURNAMENT


class CanViewTournament(HasTournamentPermission):
    required_permission = Permission.VIEW_TOURNAMENT


class CanManageParticipants(HasTournamentPermission):
    required_permission = Permission.MANAGE_PARTICIPANTS


class CanManageRounds(HasTournamentPermission):
    required_permission = Permission.MANAGE_ROUNDS


class CanSetResults(HasTournamentPermission):
    required_permission = Permission.SET_RESULTS


class CanManageAssignments(HasTournamentPermission):
    required_permission = Permission.MANAGE_ROUNDS


class CanManageRoundsOrReadOnly(HasTournamentPermissionOrReadOnly):
    required_permission = Permission.MANAGE_ROUNDS


CanEditTournamentOrReadOnly = CanManageRoundsOrReadOnly


class CanRegisterTeamForTournament(BasePermission):
    message = 'Platform admins cannot register teams for tournaments.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and not is_platform_admin(user))


class IsTeamMemberPermission(BasePermission):
    message = 'Team membership is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and TeamMember.objects.filter(user=user).exists())


class IsPlatformAdminOrTeamMemberPermission(BasePermission):
    message = 'Tournament view permission or team membership is required.'

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
        if user_has_permission(user, Permission.VIEW_TOURNAMENT):
            return True

        team_id = self._extract_team_id(request, view)
        if team_id is not None:
            return self._is_team_captain_or_member(user, team_id)

        return Team.objects.filter(
            Q(captain_id=user.id) | Q(team_members__user_id=user.id)
        ).exists()
