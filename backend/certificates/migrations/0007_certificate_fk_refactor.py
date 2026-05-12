from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0006_certificate_template'),
        ('accounts', '0003_roleactivationcode'),
        ('teams', '0004_alter_team_captain_alter_teaminvitation_invited_by'),
        ('tournaments', '0014_seed_default_icons'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates', to='teams.team'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='tournaments.tournament'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='accounts.user'),
        ),
        migrations.RemoveField(
            model_name='certificate',
            name='full_name',
        ),
        migrations.RemoveField(
            model_name='certificate',
            name='team_name',
        ),
        migrations.RemoveField(
            model_name='certificate',
            name='tournament_name',
        ),
    ]
