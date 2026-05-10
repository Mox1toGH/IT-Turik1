from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tournaments', '0017_tournamentteamregistration_is_disqualified'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to='tournament_banners/'),
        ),
    ]
