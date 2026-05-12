from django.conf import settings
from django.db import models


class Team(models.Model):
    VISIBILITY_PUBLIC = True
    VISIBILITY_PRIVATE = False

    name = models.CharField(max_length=255)
    email = models.EmailField()
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='captained_teams')
    is_public = models.BooleanField(default=False)
    organization = models.CharField(max_length=255, blank=True)
    contact_telegram = models.CharField(max_length=100, blank=True)
    contact_discord = models.CharField(max_length=100, blank=True)
    banner = models.ImageField(upload_to='team_banners/', blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='TeamMember', related_name='teams')

    class Meta:
        db_table = 'accounts_team'

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_members')

    class Meta:
        db_table = 'accounts_teammember'
        unique_together = (('user', 'team'),)
        indexes = [
            models.Index(fields=['user', 'team'], name='team_members_index_0'),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.team_id}'


class TeamInvitation(models.Model):
    STATUS_INVITED = 'invited'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'

    STATUS_CHOICES = (
        (STATUS_INVITED, 'Invited'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
    )

    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='invitations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_invitations')
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_invitations_sent',
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_INVITED)
    responded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_teaminvitation'
        unique_together = (('team', 'user'),)
        indexes = [
            models.Index(fields=['team', 'status'], name='team_invite_idx_0'),
            models.Index(fields=['user', 'status'], name='team_invite_idx_1'),
        ]

    def __str__(self):
        return f'invitation:{self.team_id}:{self.user_id}:{self.status}'


class TeamJoinRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
    )

    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_join_requests')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='team_join_requests_reviewed',
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_teamjoinrequest'
        unique_together = (('team', 'user'),)
        indexes = [
            models.Index(fields=['team', 'status'], name='team_joinreq_idx_0'),
            models.Index(fields=['user', 'status'], name='team_joinreq_idx_1'),
        ]

    def __str__(self):
        return f'join-request:{self.team_id}:{self.user_id}:{self.status}'
