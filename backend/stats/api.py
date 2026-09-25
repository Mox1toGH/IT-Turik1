from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from accounts.models import User
from backend.auth import JWTAuth
from backend.permissions import is_platform_admin
from evaluation.models import LeaderboardEntry, SubmissionEvaluation
from teams.models import Team
from tournaments.models import Submission, Tournament, TournamentTeamRegistration

from backend.schemas import ErrorResponse
from .schemas import AdminStatsResponse, PlayerStatsResponse, TeamStatsResponse, TournamentStatsResponse

router = Router(tags=['stats'], auth=JWTAuth())


def _round2(value):
    return round(float(value), 2) if value is not None else 0.0


def _win_rate(wins, total):
    return round(wins / total * 100, 2) if total else 0.0


def _team_results(team):
    entries = LeaderboardEntry.objects.filter(team=team, round__isnull=True)
    total = entries.values('tournament_id').distinct().count()
    wins = entries.filter(rank=1).values('tournament_id').distinct().count()
    
    return total, wins, max(total - wins, 0)


@router.get('/player', operation_id='getPlayerStats', response={200: PlayerStatsResponse, 401: ErrorResponse})
def get_player_stats(request):
    teams = Team.objects.filter(Q(captain=request.auth) | Q(team_members__user=request.auth)).distinct()
    team = teams.order_by('id').first()
    
    tournament_ids = TournamentTeamRegistration.objects.filter(team__in=teams, is_active=True).values_list('tournament_id', flat=True).distinct()
    total = tournament_ids.count()
    
    wins = LeaderboardEntry.objects.filter(round__isnull=True, rank=1, team__in=teams).values('tournament_id').distinct().count()
    average = SubmissionEvaluation.objects.filter(assignment__submission__team__in=teams).aggregate(value=Avg('final_score'))['value']
    
    return PlayerStatsResponse.model_validate(
        {
            'total_tournaments': total,
            'wins': wins,
            'losses': max(total - wins, 0),
            'win_rate': _win_rate(wins, total),
            'average_evaluation_score': _round2(average),
            'current_team_name': team.name if team else None,
        }
    )


@router.get('/team/{team_id}', operation_id='getTeamStats', response={200: TeamStatsResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_team_stats(request, team_id: int):
    team = get_object_or_404(Team.objects.prefetch_related('members'), pk=team_id)
    
    if request.auth.id != team.captain_id and not team.members.filter(id=request.auth.id).exists() and not is_platform_admin(request.auth):
        raise HttpError(403, 'Only team members or admins can view team stats.')
    
    total, wins, losses = _team_results(team)
    members = list(team.members.all())
    top_player = None
    
    if members:
        scores = []
        for player in members:
            average = SubmissionEvaluation.objects.filter(assignment__submission__team=team, assignment__submission__created_by=player).aggregate(value=Avg('final_score'))['value']
            scores.append({'id': player.id, 'username': player.username, 'average_evaluation_score': _round2(average)})    
        top_player = max(scores, key=lambda item: (item['average_evaluation_score'], -item['id']))
    
    average = SubmissionEvaluation.objects.filter(assignment__submission__team=team).aggregate(value=Avg('final_score'))['value']
    
    return TeamStatsResponse.model_validate(
        {
            'team_id': team.id,
            'team_name': team.name,
            'total_tournaments': total,
            'wins': wins,
            'losses': losses,
            'win_rate': _win_rate(wins, total),
            'average_member_evaluation_score': _round2(average),
            'active_members_count': len(members),
            'top_player': top_player,
        }
    )


@router.get('/tournament/{tournament_id}', operation_id='getTournamentStats', response={200: TournamentStatsResponse, 401: ErrorResponse, 403: ErrorResponse, 404: ErrorResponse})
def get_tournament_stats(request, tournament_id: int):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    if not (is_platform_admin(request.auth) or tournament.created_by_id == request.auth.id):
        raise HttpError(403, 'Only organizer or admin can view tournament stats.')
    
    registrations = TournamentTeamRegistration.objects.filter(tournament=tournament, is_active=True)
    team_ids = list(registrations.values_list('team_id', flat=True))
    total = len(team_ids)
    submissions = Submission.objects.filter(round__tournament=tournament)
    average = SubmissionEvaluation.objects.filter(assignment__submission__round__tournament=tournament).aggregate(value=Avg('final_score'))['value']
    top = LeaderboardEntry.objects.filter(tournament=tournament, round__isnull=True).select_related('team').order_by('rank', '-average_score')[:3]
    
    return TournamentStatsResponse.model_validate(
        {
            'tournament_id': tournament.id,
            'tournament_name': tournament.name,
            'total_registered_teams': total,
            'total_registered_players': User.objects.filter(
                teams__id__in=team_ids
            ).distinct().count(),
            'fill_rate': _win_rate(total, tournament.max_teams or 0),
            'completed_matches': submissions.filter(
                jury_assignments__evaluation__isnull=False
            ).distinct().count(),
            'total_matches': submissions.count(),
            'average_evaluation_score': _round2(average),
            'top_teams': [
                {
                    'team_id': entry.team_id,
                    'team_name': entry.team.name,
                    'rank': entry.rank,
                    'average_score': _round2(entry.average_score),
                }
                for entry in top
            ],
        }
    )

@router.get('/admin', operation_id='getAdminStats', response={200: AdminStatsResponse, 401: ErrorResponse, 403: ErrorResponse})
def get_admin_stats(request):
    if not is_platform_admin(request.auth):
        raise HttpError(403, 'Admin access required.')
    
    now = timezone.now()
    
    return AdminStatsResponse.model_validate(
        {
            'total_users': User.objects.count(),
            'total_teams': Team.objects.count(),
            'total_tournaments': Tournament.objects.count(),
            'new_registrations_last_7_days': User.objects.filter(
                date_joined__gte=now - timedelta(days=7)
            ).count(),
            'new_registrations_last_30_days': User.objects.filter(
                date_joined__gte=now - timedelta(days=30)
            ).count(),
            'active_tournaments': Tournament.objects.filter(
                status__in=[
                    Tournament.STATUS_REGISTRATION,
                    Tournament.STATUS_RUNNING,
                ]
            ).count(),
            'users_by_role': list(
                User.objects.values('role')
                .annotate(count=Count('id'))
                .order_by('role')
            ),
            'total_evaluation_records': SubmissionEvaluation.objects.count(),
        }
    )
