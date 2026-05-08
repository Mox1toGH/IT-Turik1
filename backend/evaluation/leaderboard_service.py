from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Avg, Sum
from rest_framework.exceptions import PermissionDenied

from tournaments.models import Round, Tournament

from .models import LeaderboardEntry, SubmissionEvaluation


def _quantize(value, digits='0.01'):
    return Decimal(value).quantize(Decimal(digits), rounding=ROUND_HALF_UP)


def compute_leaderboard(round_id: int) -> list[dict]:
    evaluations = (
        SubmissionEvaluation.objects.filter(assignment__submission__round_id=round_id)
        .select_related('assignment__submission__team', 'assignment__jury')
        .annotate(
            team_total_score=Sum('assignment__submission__jury_assignments__evaluation__total_score'),
            team_average_score=Avg('assignment__submission__jury_assignments__evaluation__final_score'),
        )
    )

    team_stats = {}
    for evaluation in evaluations:
        team = evaluation.assignment.submission.team
        stats = team_stats.setdefault(
            team.id,
            {
                'team_id': team.id,
                'team_name': team.name,
                'total_score': _quantize(evaluation.team_total_score or 0),
                'average_score': _quantize(evaluation.team_average_score or 0),
                'criteria_breakdown_raw': defaultdict(Decimal),
                'jury_breakdown': {},
            },
        )

        for score_item in evaluation.scores or []:
            criterion_name = score_item.get('criterion_name') or score_item.get('criterion_id')
            if not criterion_name:
                continue
            stats['criteria_breakdown_raw'][criterion_name] += Decimal(str(score_item.get('score', 0)))

        jury_label = evaluation.assignment.jury.full_name or evaluation.assignment.jury.username
        stats['jury_breakdown'][jury_label] = float(_quantize(evaluation.final_score or 0))

    ranked = sorted(
        team_stats.values(),
        key=lambda item: (-item['total_score'], -item['average_score'], item['team_name']),
    )

    result = []
    for idx, item in enumerate(ranked, start=1):
        result.append(
            {
                'rank': idx,
                'team_id': item['team_id'],
                'team_name': item['team_name'],
                'total_score': float(item['total_score']),
                'average_score': float(item['average_score']),
                'criteria_breakdown': {
                    key: float(_quantize(value))
                    for key, value in item['criteria_breakdown_raw'].items()
                },
                'jury_breakdown': item['jury_breakdown'],
            }
        )
    return result


def save_leaderboard_snapshot(tournament_id: int, round_id: int) -> None:
    if LeaderboardEntry.objects.filter(tournament_id=tournament_id, round_id=round_id).exists():
        pass
    else:
        rankings = compute_leaderboard(round_id)
        if rankings:
            entries = [
                LeaderboardEntry(
                    tournament_id=tournament_id,
                    round_id=round_id,
                    team_id=row['team_id'],
                    rank=row['rank'],
                    total_score=row['total_score'],
                    average_score=row['average_score'],
                    criteria_breakdown=row['criteria_breakdown'],
                    jury_breakdown=row['jury_breakdown'],
                )
                for row in rankings
            ]
            LeaderboardEntry.objects.bulk_create(entries)

    if LeaderboardEntry.objects.filter(tournament_id=tournament_id, round__isnull=True).exists():
        return

    tournament_rankings = compute_tournament_leaderboard(tournament_id)
    if not tournament_rankings:
        return

    tournament_entries = [
        LeaderboardEntry(
            tournament_id=tournament_id,
            round_id=None,
            team_id=row['team_id'],
            rank=row['rank'],
            total_score=row['total_score'],
            average_score=0,
            criteria_breakdown={},
            jury_breakdown=None,
            rounds_breakdown=row['rounds'],
        )
        for row in tournament_rankings
    ]
    LeaderboardEntry.objects.bulk_create(tournament_entries)


def get_leaderboard(round_id: int, requesting_user) -> list[dict]:
    round_obj = Round.objects.select_related('tournament').filter(id=round_id).first()
    if round_obj is None:
        return []

    is_privileged = requesting_user.role in {'admin', 'organizer', 'jury'}

    if round_obj.tournament.status == Tournament.STATUS_FINISHED:
        rows = (
            LeaderboardEntry.objects.filter(round_id=round_id)
            .select_related('team')
            .order_by('rank')
        )
        result = [
            {
                'rank': row.rank,
                'team_id': row.team_id,
                'team_name': row.team.name,
                'total_score': float(row.total_score),
                'average_score': float(row.average_score),
                'criteria_breakdown': row.criteria_breakdown,
                'jury_breakdown': row.jury_breakdown,
            }
            for row in rows
        ]
    elif round_obj.status == Round.STATUS_EVALUATED:
        result = compute_leaderboard(round_id)
    else:
        if not is_privileged:
            raise PermissionDenied('Leaderboard is not available for this round yet.')
        result = compute_leaderboard(round_id)

    if requesting_user.role == 'team':
        for row in result:
            row['jury_breakdown'] = None
    return result


def compute_tournament_leaderboard(tournament_id: int) -> list[dict]:
    rounds = (
        Round.objects.filter(tournament_id=tournament_id)
        .order_by('start_date', 'id')
        .only('id', 'name', 'status')
    )

    teams = {}
    for round_obj in rounds:
        round_ranking = compute_leaderboard(round_obj.id)
        for team_row in round_ranking:
            team_bucket = teams.setdefault(
                team_row['team_id'],
                {
                    'team_id': team_row['team_id'],
                    'team_name': team_row['team_name'],
                    'total_score': Decimal('0.00'),
                    'rounds': [],
                },
            )
            team_bucket['total_score'] += Decimal(str(team_row['total_score']))
            team_bucket['rounds'].append(
                {
                    'round_id': round_obj.id,
                    'round_name': round_obj.name,
                    'total_score': team_row['total_score'],
                    'average_score': team_row['average_score'],
                    'criteria_breakdown': team_row['criteria_breakdown'],
                    'jury_breakdown': team_row['jury_breakdown'],
                }
            )

    rankings = sorted(
        teams.values(),
        key=lambda item: (-item['total_score'], item['team_name']),
    )
    result = []
    for idx, row in enumerate(rankings, start=1):
        result.append(
            {
                'rank': idx,
                'team_id': row['team_id'],
                'team_name': row['team_name'],
                'total_score': float(_quantize(row['total_score'])),
                'rounds': row['rounds'],
            }
        )
    return result


def get_tournament_leaderboard(tournament_id: int, requesting_user) -> list[dict]:
    tournament = Tournament.objects.filter(id=tournament_id).first()
    if tournament is None:
        return []

    is_privileged = requesting_user.role in {'admin', 'organizer', 'jury'}
    has_evaluated_rounds = Round.objects.filter(
        tournament_id=tournament_id,
        status=Round.STATUS_EVALUATED,
    ).exists()

    if tournament.status == Tournament.STATUS_FINISHED:
        rows = LeaderboardEntry.objects.filter(
            tournament_id=tournament_id,
            round__isnull=True,
        ).select_related('team').order_by('rank')
        result = [
            {
                'rank': row.rank,
                'team_id': row.team_id,
                'team_name': row.team.name,
                'total_score': float(row.total_score),
                'rounds': row.rounds_breakdown or [],
            }
            for row in rows
        ]
    elif has_evaluated_rounds:
        result = compute_tournament_leaderboard(tournament_id)
    else:
        if not is_privileged:
            raise PermissionDenied('Tournament leaderboard is not available yet.')
        result = compute_tournament_leaderboard(tournament_id)

    if requesting_user.role == 'team':
        for row in result:
            for round_row in row['rounds']:
                round_row['jury_breakdown'] = None
    return result
