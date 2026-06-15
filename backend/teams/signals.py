from django.dispatch import Signal

# Signal sent when an invitation is received (created)
# invitation: TeamInvitation instance
invitation_received = Signal()

# Signal sent when an invitation is responded to (accepted/declined)
# invitation: TeamInvitation instance
invitation_responded = Signal()

# Signal sent when a join request is received (created)
# join_request: TeamJoinRequest instance
join_request_received = Signal()

# Signal sent when a join request is responded to (accepted/declined)
# join_request: TeamJoinRequest instance
join_request_responded = Signal()

# Signal sent when a member is removed by the captain
# team: Team instance
# user: User instance (the one removed)
member_removed = Signal()

# Signal sent when a member leaves the team voluntarily
# team: Team instance
# user: User instance (the one leaving)
member_left = Signal()
