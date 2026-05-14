from django.dispatch import Signal

# Signal sent when a team is registered for a tournament
# tournament: Tournament instance
# team: Team instance
# actor: User instance (captain who registered)
tournament_team_registered = Signal()

# Signal sent when a team leaves a tournament
# tournament: Tournament instance
# team: Team instance
# actor: User instance (captain who left)
tournament_team_left = Signal()

# Signal sent when a team is disqualified from a tournament
# tournament: Tournament instance
# team: Team instance
# disqualification_reason: str
tournament_team_disqualified = Signal()

# Signal sent when a round becomes active (started)
# round_obj: Round instance
round_started = Signal()

# Signal sent when a round's submissions are closed
# round_obj: Round instance
round_submission_closed = Signal()

# Signal sent when a round is marked as evaluated
# round_obj: Round instance
round_evaluated = Signal()

# Signal sent when a tournament is finished
# tournament: Tournament instance
tournament_finished = Signal()
