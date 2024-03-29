# Generated by Django 2.2.5 on 2019-10-25 12:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientrecords', '0007_auto_20191003_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeseries',
            name='data',
            field=models.FileField(upload_to='timeseries/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['txt'])]),
        ),
        migrations.AlterField(
            model_name='videos',
            name='data',
            field=models.FileField(upload_to='videos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4'])]),
        ),
    ]
