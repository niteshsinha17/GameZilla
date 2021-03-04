# Generated by Django 3.1.3 on 2021-03-04 10:12

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.PositiveIntegerField(default=0)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('P', 'Prefer not to say')], max_length=1)),
                ('DOB', models.DateField(default=datetime.datetime(2021, 3, 4, 10, 12, 14, 851073, tzinfo=utc))),
                ('TotalPlayCount', models.PositiveIntegerField(default=0)),
                ('MatchesWon', models.PositiveIntegerField(default=0)),
                ('MatchesDraw', models.PositiveIntegerField(default=0)),
                ('MatchesLost', models.PositiveIntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='Profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
