# Generated by Django 2.2.5 on 2019-09-25 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientrecords', '0002_auto_20190925_0417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diagnosisperm',
            name='perm_value',
            field=models.PositiveSmallIntegerField(choices=[(1, 'No Access'), (2, 'Read Only Access'), (3, 'Read & Set Permissions Access'), (4, 'Owner')]),
        ),
        migrations.AlterField(
            model_name='documentsperm',
            name='perm_value',
            field=models.PositiveSmallIntegerField(choices=[(1, 'No Access'), (2, 'Read Only Access'), ('3', 'Read & Set Permissions Access'), (4, 'Owner')]),
        ),
        migrations.AlterField(
            model_name='imagesperm',
            name='perm_value',
            field=models.PositiveSmallIntegerField(choices=[(1, 'No Access'), (2, 'Read Only Access'), ('3', 'Read & Set Permissions Access'), (4, 'Owner')]),
        ),
        migrations.AlterField(
            model_name='readingsperm',
            name='perm_value',
            field=models.PositiveSmallIntegerField(choices=[(1, 'No Access'), (2, 'Read Only Access'), ('3', 'Read & Set Permissions Access'), (4, 'Owner')]),
        ),
        migrations.AlterField(
            model_name='timeseriesperm',
            name='perm_value',
            field=models.PositiveSmallIntegerField(choices=[(1, 'No Access'), (2, 'Read Only Access'), ('3', 'Read & Set Permissions Access'), (4, 'Owner')]),
        ),
        migrations.AlterField(
            model_name='videosperm',
            name='perm_value',
            field=models.PositiveSmallIntegerField(choices=[(1, 'No Access'), (2, 'Read Only Access'), ('3', 'Read & Set Permissions Access'), (4, 'Owner')]),
        ),
    ]