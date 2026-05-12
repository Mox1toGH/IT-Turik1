from django.conf import settings
from django.db import models

from teams.models import Team
from tournaments.models import Round, Tournament


class JuryAssignment(models.Model):
    submission = models.ForeignKey('tournaments.Submission', on_delete=models.CASCADE, related_name='jury_assignments')
    jury = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jury_assignments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('submission', 'jury')

    def __str__(self):
        return f'Assignment:{self.submission_id}:{self.jury_id}'


class SubmissionEvaluation(models.Model):
    assignment = models.OneToOneField(JuryAssignment, on_delete=models.CASCADE, related_name='evaluation')
    scores = models.JSONField(default=list)
    total_score = models.PositiveIntegerField(default=0, editable=False)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Evaluation:{self.assignment_id}:{self.final_score}'

    def save(self, *args, **kwargs):
        scores_list = [item.get('score', 0) for item in self.scores] if self.scores else []
        self.total_score = sum(scores_list)
        self.final_score = sum(scores_list) / len(scores_list) if scores_list else 0
        super().save(*args, **kwargs)


class LeaderboardEntry(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='leaderboard_entries')
    round = models.ForeignKey(Round, null=True, blank=True, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()
    total_score = models.DecimalField(max_digits=10, decimal_places=2)
    average_score = models.DecimalField(max_digits=6, decimal_places=2)
    criteria_breakdown = models.JSONField()
    jury_breakdown = models.JSONField(null=True, blank=True)
    rounds_breakdown = models.JSONField(null=True, blank=True)
    snapshot_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']
        unique_together = [('tournament', 'round', 'team')]
