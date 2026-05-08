from django.db import models
import uuid
import os


class CertificateTemplate(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='certificate_templates/')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other templates to not default
            CertificateTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the image file from storage
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class Certificate(models.Model):
    unique_code = models.CharField(max_length=36, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    participant_name_snapshot = models.CharField(max_length=255, blank=True, default='')
    team_name_snapshot = models.CharField(max_length=255, blank=True, default='')
    tournament_name_snapshot = models.CharField(max_length=255, blank=True, default='')
    placement = models.CharField(max_length=100)
    certificate_number = models.CharField(max_length=100)
    template = models.ForeignKey(CertificateTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def _resolve_participant_name(self):
        if not self.user:
            return ''
        return (self.user.full_name or self.user.username).strip()

    def _resolve_team_name(self):
        if not self.team:
            return ''
        return self.team.name

    def _resolve_tournament_name(self):
        if not self.tournament:
            return ''
        return self.tournament.name

    def fill_snapshot_fields(self, *, force=False):
        if force or not self.participant_name_snapshot:
            self.participant_name_snapshot = self._resolve_participant_name()

        if force or not self.team_name_snapshot:
            self.team_name_snapshot = self._resolve_team_name()

        if force or not self.tournament_name_snapshot:
            self.tournament_name_snapshot = self._resolve_tournament_name()

    def save(self, *args, **kwargs):
        # Immutable snapshot for certificate data:
        # on create we always capture current names;
        # on update we only backfill empty snapshots.
        self.fill_snapshot_fields(force=self._state.adding)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.participant_name_snapshot or self._resolve_participant_name()

    @property
    def team_name(self):
        return self.team_name_snapshot or self._resolve_team_name()

    @property
    def tournament_name(self):
        return self.tournament_name_snapshot or self._resolve_tournament_name()

    def __str__(self):
        tournament_name = self.tournament_name or 'No tournament'
        return f"{self.full_name} - {tournament_name}"
