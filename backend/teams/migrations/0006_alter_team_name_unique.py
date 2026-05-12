from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_team_banner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
