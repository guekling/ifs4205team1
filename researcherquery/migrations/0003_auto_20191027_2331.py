# Generated by Django 2.2.5 on 2019-10-27 15:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('researcherquery', '0002_auto_20191027_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='safeusers',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]