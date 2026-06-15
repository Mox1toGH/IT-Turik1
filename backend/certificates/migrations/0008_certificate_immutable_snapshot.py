from django.db import migrations, models
import django.db.models.deletion


def backfill_snapshots(apps, schema_editor):
    Certificate = apps.get_model('certificates', 'Certificate')

    for certificate in Certificate.objects.select_related('user', 'team', 'tournament').iterator():
        participant_name = ''
        if certificate.user_id and certificate.user:
            participant_name = ((certificate.user.full_name or certificate.user.username) or '').strip()

        team_name = certificate.team.name if certificate.team_id and certificate.team else ''
        tournament_name = certificate.tournament.name if certificate.tournament_id and certificate.tournament else ''

        Certificate.objects.filter(pk=certificate.pk).update(
            participant_name_snapshot=participant_name,
            team_name_snapshot=team_name,
            tournament_name_snapshot=tournament_name,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0007_certificate_fk_refactor'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='participant_name_snapshot',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='certificate',
            name='team_name_snapshot',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='certificate',
            name='tournament_name_snapshot',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.RunPython(backfill_snapshots, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='certificate',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates', to='teams.team'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates', to='tournaments.tournament'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates', to='accounts.user'),
        ),
    ]
