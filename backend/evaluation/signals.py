from django.dispatch import Signal

# Signal sent when jury assignments are created/replaced for a round
# round_obj: Round instance
# jury_users: list of User instances (the jury members assigned)
jury_assignments_created = Signal()
