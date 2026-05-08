from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Tournament(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_REGISTRATION = 'registration'
    STATUS_RUNNING = 'running'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_REGISTRATION, 'Registration'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_FINISHED, 'Finished'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_teams = models.PositiveIntegerField(blank=True, null=True)
    min_team_members = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_tournaments',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            errors['end_date'] = 'end_date must be greater than start_date.'

        if self.min_team_members is not None and self.min_team_members < 1:
            errors['min_team_members'] = 'min_team_members must be at least 1.'

        if self.max_teams is not None and self.max_teams < 1:
            errors['max_teams'] = 'max_teams must be at least 1.'

        if errors:
            raise ValidationError(errors)


class Round(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_SUBMISSION_CLOSED = 'submission_closed'
    STATUS_EVALUATED = 'evaluated'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SUBMISSION_CLOSED, 'SubmissionClosed'),
        (STATUS_EVALUATED, 'Evaluated'),
    )

    EVALUATION_SCORE = 'score'

    EVALUATION_CRITERIA_CHOICES = (
        (EVALUATION_SCORE, 'Score'),
    )

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    name = models.CharField(max_length=255, blank=True)
    description = models.JSONField(default=dict, blank=True)
    tech_requirements = models.JSONField(default=dict, blank=True)
    must_have_requirements = models.JSONField(default=dict, blank=True)
    criteria = models.JSONField(default=list, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    passing_count = models.PositiveIntegerField(blank=True, null=True)
    evaluation_criteria = models.CharField(
        max_length=32,
        choices=EVALUATION_CRITERIA_CHOICES,
        default=EVALUATION_SCORE,
    )
    materials = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('tournament_id', 'start_date')
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'start_date'],
                name='uniq_round_tournament_start_date',
            ),
            models.UniqueConstraint(
                fields=['tournament'],
                condition=Q(status='active'),
                name='uniq_active_round_per_tournament',
            ),
        ]

    def __str__(self):
        return f'{self.tournament_id}:{self.name or self.default_name}'

    @property
    def default_name(self):
        pos = self.position
        return f'Round {pos}' if pos else 'Round'

    @property
    def position(self):
        ids = list(
            Round.objects.filter(tournament_id=self.tournament_id)
            .order_by('start_date')
            .values_list('id', flat=True)
        )
        try:
            return ids.index(self.pk) + 1
        except ValueError:
            return None

    @property
    def is_submission_open(self):
        return self.status == self.STATUS_ACTIVE

    def _validate_date_overlaps(self, errors):
        if not self.tournament_id or not self.start_date or not self.end_date:
            return

        overlaps = Round.objects.filter(
            tournament_id=self.tournament_id,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        ).exclude(pk=self.pk)

        if overlaps.exists():
            errors['start_date'] = 'Round dates overlap with another round in this tournament.'

    @staticmethod
    def _normalize_for_compare(value):
        if value is None:
            return None
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def clean(self):
        errors = {}

        start_date = self._normalize_for_compare(self.start_date)
        end_date = self._normalize_for_compare(self.end_date)

        if start_date and end_date and start_date >= end_date:
            errors['end_date'] = 'end_date must be greater than start_date.'

        tournament = getattr(self, 'tournament', None)
        tournament_start = self._normalize_for_compare(getattr(tournament, 'start_date', None))
        tournament_end = self._normalize_for_compare(getattr(tournament, 'end_date', None))

        if tournament and start_date and end_date and tournament_start and tournament_end:
            # Inclusive boundaries: round may start at tournament start and end at tournament end.
            if start_date < tournament_start or end_date > tournament_end:
                errors['start_date'] = 'Round dates must be within tournament dates.'

        self._validate_date_overlaps(errors)

        if not isinstance(self.criteria, list):
            errors['criteria'] = 'Criteria must be a list.'
        else:
            seen_ids = set()
            for idx, c in enumerate(self.criteria):
                if not isinstance(c, dict):
                    errors['criteria'] = f'Item at index {idx} must be an object.'
                    break
                
                c_id = c.get('id')
                name = c.get('name')
                max_score = c.get('max_score')
                
                if not c_id or not isinstance(c_id, str):
                    errors['criteria'] = f'Item at index {idx} must have a valid string "id".'
                    break
                if not name or not isinstance(name, str):
                    errors['criteria'] = f'Item "{c_id}" must have a valid string "name".'
                    break
                if max_score is None or not isinstance(max_score, (int, float)) or max_score <= 0:
                    errors['criteria'] = f'Item "{c_id}" must have a positive "max_score".'
                    break
                    
                if c_id in seen_ids:
                    errors['criteria'] = f'Duplicate criteria id: "{c_id}".'
                    break
                seen_ids.add(c_id)

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.default_name
        super().save(*args, **kwargs)


class Submission(models.Model):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='submissions')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='submissions')
    github_url = models.URLField()
    demo_video_url = models.URLField(blank=True)
    demo_video_file = models.FileField(upload_to='tournaments/demo_videos/', blank=True)
    live_demo_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_submissions',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)
        constraints = [
            models.UniqueConstraint(fields=['team', 'round'], name='uniq_submission_team_round'),
        ]

    def __str__(self):
        return f'{self.team_id}:{self.round_id}'

    def clean(self):
        errors = {}

        if not self.github_url:
            errors['github_url'] = 'github_url is required.'

        if not self.demo_video_url and not self.demo_video_file:
            errors['demo_video_url'] = 'Provide demo_video_url or demo_video_file.'

        if self.round and self.round.status != Round.STATUS_ACTIVE:
            errors['round'] = 'Round is closed for submissions.'

        if errors:
            raise ValidationError(errors)


class TournamentTeamRegistration(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='team_registrations',
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='tournament_registrations',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_tournament_team_registrations',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'team'],
                name='uniq_tournament_team_registration',
            ),
        ]

    def __str__(self):
        return f'{self.tournament_id}:{self.team_id}'


class Icon(models.Model):
    name = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=500)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name or self.path


class Event(models.Model):
    TYPE_MEET = 'meet'
    TYPE_EVENT = 'event'

    TYPE_CHOICES = (
        (TYPE_MEET, 'Meet'),
        (TYPE_EVENT, 'Event'),
    )

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='events',
    )
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)
    start_datetime = models.DateTimeField()
    icon = models.ForeignKey(
        Icon,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='events',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('start_datetime',)

    def __str__(self):
        return f'{self.tournament_id}:{self.title}'

