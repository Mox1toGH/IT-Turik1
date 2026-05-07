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
}
