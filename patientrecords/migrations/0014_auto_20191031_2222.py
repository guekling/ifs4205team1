# Generated by Django 2.2.6 on 2019-10-31 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientrecords', '0013_auto_20191031_2132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notifications',
            name='status',
        ),
        migrations.AlterField(
            model_name='notifications',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)]),
        ),
        migrations.AddField(
            model_name='notifications',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)]),
        ),
    ]
