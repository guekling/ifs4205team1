# Generated by Django 2.2.6 on 2019-11-08 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QiInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combi_age', models.CharField(max_length=3)),
                ('combi_postalcode', models.CharField(max_length=2)),
                ('combi_date', models.CharField(max_length=2)),
                ('k_value', models.PositiveIntegerField()),
                ('suppression_rate', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='SafeUsers',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('age', models.CharField(max_length=8)),
                ('postalcode', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='SafeVideos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='researcherquery.SafeUsers')),
            ],
        ),
        migrations.CreateModel(
            name='SafeReadings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=16)),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='researcherquery.SafeUsers')),
            ],
        ),
        migrations.CreateModel(
            name='SafeImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='researcherquery.SafeUsers')),
            ],
        ),
        migrations.CreateModel(
            name='SafeDiagnosis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=64)),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='researcherquery.SafeUsers')),
            ],
        ),
    ]
