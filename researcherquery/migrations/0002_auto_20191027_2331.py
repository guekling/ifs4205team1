# Generated by Django 2.2.5 on 2019-10-27 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researcherquery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='safeusers',
            name='uid',
            field=models.CharField(editable=False, max_length=6, primary_key=True, serialize=False),
        ),
    ]