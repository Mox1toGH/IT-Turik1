from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('teams', '0004_alter_team_captain_alter_teaminvitation_invited_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to='team_banners/'),
        ),
    ]
