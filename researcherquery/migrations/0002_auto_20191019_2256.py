# Generated by Django 2.2.5 on 2019-10-19 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researcherquery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qiinfo',
            name='combi_age',
            field=models.CharField(max_length=3),
        ),
    ]
