from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0002_pointstransaction_order'),
        ('tournaments', '0001_initial'),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TournamentPointsAward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('award_type', models.CharField(choices=[('participation', 'Participation'), ('placement', 'Placement')], max_length=32)),
                ('rank', models.PositiveIntegerField(blank=True, null=True)),
                ('amount', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_points_awards', to='tournaments.tournament')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_points_awards', to='teams.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_points_awards', to='accounts.user')),
            ],
            options={
                'ordering': ('-created_at', '-id'),
            },
        ),
        migrations.AddConstraint(
            model_name='tournamentpointsaward',
            constraint=models.UniqueConstraint(fields=('user', 'tournament', 'award_type'), name='uniq_tournament_points_award'),
        ),
    ]
