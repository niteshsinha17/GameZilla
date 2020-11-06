# Generated by Django 3.0.5 on 2020-11-03 15:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0005_auto_20201031_2035'),
    ]

    operations = [
        migrations.CreateModel(
            name='TAC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.SlugField()),
                ('started', models.BooleanField(default=False)),
                ('max_player', models.IntegerField(default=0)),
                ('board', jsonfield.fields.JSONField(null=True)),
                ('current', models.IntegerField(blank=True, null=True)),
                ('players_entered', models.IntegerField(default=0)),
                ('time_stamp', models.FloatField(blank=True, null=True)),
                ('round', models.IntegerField(blank=True, null=True)),
                ('cross', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cross', to=settings.AUTH_USER_MODEL)),
                ('current_player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('room', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='game.Room')),
                ('zero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zero', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
