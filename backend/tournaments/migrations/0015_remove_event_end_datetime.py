from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('tournaments', '0014_seed_default_icons'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='end_datetime',
        ),
    ]
