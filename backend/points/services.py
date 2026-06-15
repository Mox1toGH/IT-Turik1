from django.db import transaction

from .models import PointsTransaction, UserPointsBalance


@transaction.atomic
def apply_points_modification(*, user, operation, reason, amount=None, order=None):
    balance_obj, _ = UserPointsBalance.objects.select_for_update().get_or_create(
        user=user,
        defaults={'balance': 0},
    )

    current_balance = balance_obj.balance

    if operation == 'add':
        delta = int(amount)
        new_balance = current_balance + delta
    elif operation == 'subtract':
        delta = -int(amount)
        new_balance = current_balance + delta
    elif operation == 'set':
        new_balance = int(amount)
        delta = new_balance - current_balance
    elif operation == 'reset':
        new_balance = 0
        delta = -current_balance
    else:
        raise ValueError('Unsupported operation.')

    balance_obj.balance = new_balance
    balance_obj.save(update_fields=['balance', 'updated_at'])

    transaction_obj = PointsTransaction.objects.create(
        user=user,
        order=order,
        amount=delta,
        reason=reason,
    )

    return balance_obj, transaction_obj


PARTICIPATION_POINTS = 10
PLACEMENT_POINTS = {
    1: 50,
    2: 30,
    3: 20,
}


def _get_team_participants(team):
    from tournaments.services import get_team_participant_ids

    user_ids = get_team_participant_ids(team=team)
    from accounts.models import User

    return User.objects.filter(id__in=user_ids)


@transaction.atomic
def award_tournament_points(*, tournament):
    from .models import TournamentPointsAward
    from tournaments.models import TournamentTeamRegistration
    from evaluation.leaderboard_service import compute_tournament_leaderboard

    if tournament.status != tournament.STATUS_FINISHED:
        return

    if TournamentPointsAward.objects.filter(tournament=tournament).exists():
        return

    registrations = TournamentTeamRegistration.objects.filter(
        tournament=tournament,
        is_active=True,
        is_disqualified=False,
    ).select_related('team')

    leaderboard = compute_tournament_leaderboard(tournament.id)
    team_rank_map = {
        row['team_id']: row['rank']
        for row in leaderboard
        if row.get('rank') in PLACEMENT_POINTS
    }

    award_records = []
    for registration in registrations:
        team = registration.team
        users = _get_team_participants(team)
        if not users.exists():
            continue

        for user in users:
            # Participation award
            apply_points_modification(
                user=user,
                operation='add',
                amount=PARTICIPATION_POINTS,
                reason=f'Tournament participation: {tournament.name}',
            )
            award_records.append(
                TournamentPointsAward(
                    user=user,
                    tournament=tournament,
                    team=team,
                    award_type='participation',
                    amount=PARTICIPATION_POINTS,
                )
            )

            # Placement award if this team placed in top positions
            rank = team_rank_map.get(team.id)
            if rank:
                amount = PLACEMENT_POINTS[rank]
                apply_points_modification(
                    user=user,
                    operation='add',
                    amount=amount,
                    reason=f'Tournament placement #{rank}: {tournament.name}',
                )
                award_records.append(
                    TournamentPointsAward(
                        user=user,
                        tournament=tournament,
                        team=team,
                        award_type='placement',
                        rank=rank,
                        amount=amount,
                    )
                )

    if award_records:
        TournamentPointsAward.objects.bulk_create(award_records)
