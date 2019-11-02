# Generated by Django 2.2.6 on 2019-11-02 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_user_lockedipaddr'),
    ]

    operations = [
        migrations.CreateModel(
            name='Locked',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lockedipaddr', models.GenericIPAddressField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='lockedipaddr',
        ),
    ]
