# Generated by Django 2.2.5 on 2019-09-25 02:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Diagnosis',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
                ('time_start', models.DateTimeField(auto_now_add=True)),
                ('time_end', models.DateTimeField()),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
                ('type', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('data', models.FileField(upload_to='media/documents/')),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('patient_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
                ('type', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('data', models.ImageField(upload_to='media/images/')),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('patient_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='Readings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('data', models.DecimalField(decimal_places=2, max_digits=10)),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('patient_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSeries',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('data', models.FileField(upload_to='media/timeseries/')),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('patient_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='Videos',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
                ('type', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('data', models.FileField(upload_to='media/videos/')),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('patient_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='VideosPerm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('perm_value', models.PositiveSmallIntegerField()),
                ('given_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Healthcare')),
                ('videos_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patientrecords.Videos')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSeriesPerm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('perm_value', models.PositiveSmallIntegerField()),
                ('given_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('timeseries_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patientrecords.TimeSeries')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Healthcare')),
            ],
        ),
        migrations.CreateModel(
            name='ReadingsPerm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('perm_value', models.PositiveSmallIntegerField()),
                ('given_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('readings_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patientrecords.Readings')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Healthcare')),
            ],
        ),
        migrations.CreateModel(
            name='ImagesPerm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('perm_value', models.PositiveSmallIntegerField()),
                ('given_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('img_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patientrecords.Images')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Healthcare')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentsPerm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('perm_value', models.PositiveSmallIntegerField()),
                ('docs_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patientrecords.Documents')),
                ('given_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Healthcare')),
            ],
        ),
        migrations.CreateModel(
            name='DiagnosisPerm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('perm_value', models.PositiveSmallIntegerField()),
                ('diag_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patientrecords.Diagnosis')),
                ('given_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Healthcare')),
            ],
        ),
    ]
