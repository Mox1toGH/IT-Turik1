from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from backend.permissions import is_platform_admin
from accounts.models import User
from teams.models import Team
from tournaments.models import Tournament, TournamentTeamRegistration, Submission, Round
from evaluation.models import SubmissionEvaluation, LeaderboardEntry

from .serializers import (
    AdminStatsSerializer,
    PlayerStatsSerializer,
    TeamStatsSerializer,
    TournamentStatsSerializer,
)


def _round2(value):
    if value is None:
        return 0.0
    return round(float(value), 2)


def _compute_win_rate(wins, total):
    if total <= 0:
        return 0.0
    return round((wins / total) * 100.0, 2)


def _team_member_ids(team):
    return list(team.members.values_list('id', flat=True).distinct())


def _team_average_evaluation_score(team):
    avg = SubmissionEvaluation.objects.filter(
        assignment__submission__team=team,
    ).aggregate(value=Avg('final_score'))['value']
    return _round2(avg)


def _team_wins_losses(team):
    # A "win" is considered rank 1 in tournament-level leaderboard snapshots.
    tournament_entries = LeaderboardEntry.objects.filter(
        team=team,
        round__isnull=True,
    )
    total = tournament_entries.values('tournament_id').distinct().count()
    wins = tournament_entries.filter(rank=1).values('tournament_id').distinct().count()
    losses = max(total - wins, 0)
    return total, wins, losses


class PlayerStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        team = Team.objects.filter(
            Q(captain=user) | Q(team_members__user=user),
        ).distinct().order_by('id').first()

        tournament_ids = TournamentTeamRegistration.objects.filter(
            team__in=Team.objects.filter(Q(captain=user) | Q(team_members__user=user)).distinct(),
            is_active=True,
        ).values_list('tournament_id', flat=True).distinct()

        total_tournaments = tournament_ids.count()

        wins = LeaderboardEntry.objects.filter(
            round__isnull=True,
            rank=1,
            team__in=Team.objects.filter(Q(captain=user) | Q(team_members__user=user)).distinct(),
        ).values('tournament_id').distinct().count()

        losses = max(total_tournaments - wins, 0)

        average_evaluation_score = SubmissionEvaluation.objects.filter(
            assignment__submission__team__in=Team.objects.filter(Q(captain=user) | Q(team_members__user=user)).distinct(),
        ).aggregate(value=Avg('final_score'))['value']

        data = {
            'total_tournaments': total_tournaments,
            'wins': wins,
            'losses': losses,
            'win_rate': _compute_win_rate(wins, total_tournaments),
            'average_evaluation_score': _round2(average_evaluation_score),
            'current_team_name': team.name if team else None,
        }
        return Response(PlayerStatsSerializer(data).data)


class TeamStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, team_id):
        team = get_object_or_404(Team.objects.prefetch_related('members'), pk=team_id)

        is_member = team.captain_id == request.user.id or team.members.filter(id=request.user.id).exists()
        if not is_member and not is_platform_admin(request.user):
            raise PermissionDenied('Only team members or admins can view team stats.')

        total_tournaments, wins, losses = _team_wins_losses(team)

        member_ids = _team_member_ids(team)
        active_members_count = len(member_ids)

        top_player = None
        if member_ids:
            players = []
            for player in User.objects.filter(id__in=member_ids).only('id', 'username'):
                avg_score = SubmissionEvaluation.objects.filter(
                    assignment__submission__team=team,
                    assignment__submission__created_by=player,
                ).aggregate(value=Avg('final_score'))['value']
                players.append({
                    'id': player.id,
                    'username': player.username,
                    'average_evaluation_score': _round2(avg_score),
                })

            players.sort(key=lambda p: (p['average_evaluation_score'], -p['id']), reverse=True)
            top_player = players[0] if players else None

        data = {
            'team_id': team.id,
            'team_name': team.name,
            'total_tournaments': total_tournaments,
            'wins': wins,
            'losses': losses,
            'win_rate': _compute_win_rate(wins, total_tournaments),
            'average_member_evaluation_score': _team_average_evaluation_score(team),
            'active_members_count': active_members_count,
            'top_player': top_player,
        }
        return Response(TeamStatsSerializer(data).data)


class TournamentStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tournament_id):
        tournament = get_object_or_404(Tournament, pk=tournament_id)

        if not (is_platform_admin(request.user) or tournament.created_by_id == request.user.id):
            raise PermissionDenied('Only organizer or admin can view tournament stats.')

        registrations = TournamentTeamRegistration.objects.filter(tournament=tournament, is_active=True)
        team_ids = list(registrations.values_list('team_id', flat=True))

        total_registered_teams = len(team_ids)
        total_registered_players = User.objects.filter(teams__id__in=team_ids).distinct().count()

        capacity = tournament.max_teams or 0
        fill_rate = _compute_win_rate(total_registered_teams, capacity) if capacity else 0.0

        submissions = Submission.objects.filter(round__tournament=tournament)
        total_matches = submissions.count()
        completed_matches = submissions.filter(
            jury_assignments__evaluation__isnull=False,
        ).distinct().count()

        average_evaluation_score = SubmissionEvaluation.objects.filter(
            assignment__submission__round__tournament=tournament,
        ).aggregate(value=Avg('final_score'))['value']

        top_entries = list(
            LeaderboardEntry.objects.filter(tournament=tournament, round__isnull=True)
            .select_related('team')
            .order_by('rank', '-average_score')[:3]
        )

        top_teams = [
            {
                'team_id': entry.team_id,
                'team_name': entry.team.name,
                'rank': entry.rank,
                'average_score': _round2(entry.average_score),
            }
            for entry in top_entries
        ]

        data = {
            'tournament_id': tournament.id,
            'tournament_name': tournament.name,
            'total_registered_teams': total_registered_teams,
            'total_registered_players': total_registered_players,
            'fill_rate': fill_rate,
            'completed_matches': completed_matches,
            'total_matches': total_matches,
            'average_evaluation_score': _round2(average_evaluation_score),
            'top_teams': top_teams,
        }
        return Response(TournamentStatsSerializer(data).data)


class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)

        users_by_role = list(
            User.objects.values('role')
            .annotate(count=Count('id'))
            .order_by('role')
        )

        data = {
            'total_users': User.objects.count(),
            'total_teams': Team.objects.count(),
            'total_tournaments': Tournament.objects.count(),
            'new_registrations_last_7_days': User.objects.filter(date_joined__gte=last_7_days).count(),
            'new_registrations_last_30_days': User.objects.filter(date_joined__gte=last_30_days).count(),
            'active_tournaments': Tournament.objects.filter(
                status__in=[Tournament.STATUS_REGISTRATION, Tournament.STATUS_RUNNING],
            ).count(),
            'users_by_role': users_by_role,
            'total_evaluation_records': SubmissionEvaluation.objects.count(),
        }

        return Response(AdminStatsSerializer(data).data)
