# Generated by Django 2.2.6 on 2019-11-02 18:30

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('userlogs', '0002_auto_20191024_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='user_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
    ]