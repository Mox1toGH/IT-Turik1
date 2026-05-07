from rest_framework.exceptions import ValidationError


def get_active_tournament_registration(team):
    """Returns active TournamentTeamRegistration or None."""
    from tournaments.models import Tournament, TournamentTeamRegistration

    return (
        TournamentTeamRegistration.objects.select_related('tournament')
        .filter(
            team=team,
            is_active=True,
            tournament__status__in=[
                Tournament.STATUS_REGISTRATION,
                Tournament.STATUS_RUNNING,
            ],
        )
        .first()
    )


def assert_team_not_in_active_tournament(team):
    if get_active_tournament_registration(team):
        raise ValidationError(
            {
                'team': (
                    'This action is not allowed while the team is participating in an active tournament.'
                )
            }
        )


def assert_can_remove_member(team):
    registration = get_active_tournament_registration(team)
    if not registration:
        return

    tournament = registration.tournament
    from tournaments.services import get_team_participant_ids

    participant_ids = get_team_participant_ids(team=team)
    current_count = len(participant_ids)
    min_required = tournament.min_team_members or 1

    if current_count <= min_required:
        raise ValidationError(
            {
                'team': (
                    f'Cannot remove member: team must have more than '
                    f'{min_required} participant(s) as required by the tournament.'
                )
            }
        )
