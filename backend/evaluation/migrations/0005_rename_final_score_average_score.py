# Generated migration to rename final_score to average_score

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0004_leaderboardentry_rounds_breakdown'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submissionevaluation',
            old_name='final_score',
            new_name='average_score',
        ),
    ]
