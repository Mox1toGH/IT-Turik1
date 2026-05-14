"""
Notification event configuration.

To change which channels an event uses, edit the 'channels' list below.
Available channels: 'system', 'email'.

  - 'system'  → saves a Notification record in the database (in-site).
  - 'email'   → sends an email to the recipient via Django's email backend.

Example — to make 'team_invitation_accepted' also send email:
    'team_invitation_accepted': {'channels': ['system', 'email']},
"""

class NotificationEvent:
    """Represents a specific notification event and its template logic."""

    def __init__(self, key, title, message, channels=None, email_subject=None):
        self.key = key
        self.title_tpl = title
        self.message_tpl = message
        self.channels = channels or ['system']
        self.email_subject_tpl = email_subject

    def format(self, context):
        """Returns formatted (title, message, email_subject) for the given context."""
        ctx = context or {}
        title = self.title_tpl.format(**ctx)
        message = self.message_tpl.format(**ctx)
        email_subject = None
        if self.email_subject_tpl:
            email_subject = self.email_subject_tpl.format(**ctx)
        return title, message, email_subject


# Registry of all supported events
EVENTS = {
    # ── Team invitations ───────────────────────────────────────────
    'team_invitation_received': NotificationEvent(
        key='team_invitation_received',
        channels=['system', 'email'],
        title='Team Invitation',
        message='You have received an invitation to join team "[team:{team_id}:{team_name}]" from [user:{user_id}:{invited_by}].',
        email_subject='Invitation to join team "{team_name}"',
    ),
    'team_invitation_accepted': NotificationEvent(
        key='team_invitation_accepted',
        channels=['system'],
        title='Invitation Accepted',
        message='[user:{user_id}:{user_name}] has accepted the invitation to join team "[team:{team_id}:{team_name}]".',
    ),
    'team_invitation_declined': NotificationEvent(
        key='team_invitation_declined',
        channels=['system'],
        title='Invitation Declined',
        message='[user:{user_id}:{user_name}] has declined the invitation to join team "[team:{team_id}:{team_name}]".',
    ),

    # ── Join requests ──────────────────────────────────────────────
    'team_join_request_received': NotificationEvent(
        key='team_join_request_received',
        channels=['system', 'email'],
        title='Join Request Received',
        message='[user:{user_id}:{user_name}] has sent a request to join team "[team:{team_id}:{team_name}]".',
        email_subject='New join request for team "{team_name}"',
    ),
    'team_join_request_accepted': NotificationEvent(
        key='team_join_request_accepted',
        channels=['system'],
        title='Join Request Approved',
        message='Your request to join team "[team:{team_id}:{team_name}]" has been approved.',
    ),
    'team_join_request_declined': NotificationEvent(
        key='team_join_request_declined',
        channels=['system'],
        title='Join Request Declined',
        message='Your request to join team "[team:{team_id}:{team_name}]" has been declined.',
    ),

    # ── Membership changes ─────────────────────────────────────────
    'team_member_removed': NotificationEvent(
        key='team_member_removed',
        channels=['system', 'email'],
        title='Removed from Team',
        message='You have been removed from team "[team:{team_id}:{team_name}]".',
        email_subject='You were removed from team "{team_name}"',
    ),
    'team_member_left': NotificationEvent(
        key='team_member_left',
        channels=['system'],
        title='Member Left Team',
        message='[user:{user_id}:{user_name}] has left team "[team:{team_id}:{team_name}]".',
    ),
    'news_published': NotificationEvent(
        key='news_published',
        channels=['system', 'email'],
        title='New Announcement',
        message='A new post was published: [news:{news_id}:{news_title}].',
        email_subject='New announcement: {news_title}',
    ),
    'tournament_certificate_issued': NotificationEvent(
        key='tournament_certificate_issued',
        channels=['system', 'email'],
        title='Certificate Issued',
        message='Your certificate for tournament "{tournament_name}" is ready.',
        email_subject='Your tournament certificate is ready',
    ),

    # ── Tournament lifecycle ────────────────────────────────────────
    'tournament_team_registered': NotificationEvent(
        key='tournament_team_registered',
        channels=['system'],
        title='Team Registered',
        message='Your team "{team_name}" has been successfully registered for tournament "[tournament:{tournament_id}:{tournament_name}]".',
    ),
    'tournament_team_left': NotificationEvent(
        key='tournament_team_left',
        channels=['system'],
        title='Team Left Tournament',
        message='Your team "{team_name}" has left the tournament "{tournament_name}".',
    ),
    'tournament_team_disqualified': NotificationEvent(
        key='tournament_team_disqualified',
        channels=['system', 'email'],
        title='Team Disqualified',
        message='Your team "{team_name}" has been disqualified from tournament "[tournament:{tournament_id}:{tournament_name}]". Reason: {reason}.',
        email_subject='Your team was disqualified from "{tournament_name}"',
    ),
    'tournament_round_started': NotificationEvent(
        key='tournament_round_started',
        channels=['system', 'email'],
        title='New Round Started',
        message='Round "{round_name}" in tournament "[tournament:{tournament_id}:{tournament_name}]" has started. Submit your project before the deadline.',
        email_subject='Round "{round_name}" has started — submit your project',
    ),
    'tournament_round_submission_closed': NotificationEvent(
        key='tournament_round_submission_closed',
        channels=['system'],
        title='Submissions Closed',
        message='Submission period for round "{round_name}" in tournament "[tournament:{tournament_id}:{tournament_name}]" is now closed.',
    ),
    'tournament_round_evaluated': NotificationEvent(
        key='tournament_round_evaluated',
        channels=['system'],
        title='Round Results Published',
        message='Results for round "{round_name}" in tournament "[tournament:{tournament_id}:{tournament_name}]" have been published.',
    ),
    'tournament_finished': NotificationEvent(
        key='tournament_finished',
        channels=['system', 'email'],
        title='Tournament Finished',
        message='Tournament "[tournament:{tournament_id}:{tournament_name}]" has finished. Check the final leaderboard!',
        email_subject='Tournament "{tournament_name}" has finished',
    ),
    'tournament_round_eliminated': NotificationEvent(
        key='tournament_round_eliminated',
        channels=['system', 'email'],
        title='Team Eliminated',
        message='Your team "{team_name}" did not advance past round "{round_name}" in tournament "[tournament:{tournament_id}:{tournament_name}]".',
        email_subject='Your team was eliminated in round "{round_name}"',
    ),

    # ── Evaluation / jury ───────────────────────────────────────────
    'jury_assignment_created': NotificationEvent(
        key='jury_assignment_created',
        channels=['system', 'email'],
        title='Jury Assignment',
        message='You have been assigned as a jury member for round "{round_name}" in tournament "[tournament:{tournament_id}:{tournament_name}]". Please submit your evaluations before the deadline.',
        email_subject='You are assigned as jury for round "{round_name}"',
    ),
}
