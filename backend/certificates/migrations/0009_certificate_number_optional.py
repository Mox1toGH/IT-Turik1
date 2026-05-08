from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0008_certificate_immutable_snapshot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='certificate_number',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
