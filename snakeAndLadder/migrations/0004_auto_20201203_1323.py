# Generated by Django 3.1.3 on 2020-12-03 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snakeAndLadder", "0003_snl_player_no"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="snl",
            name="player_no",
        ),
        migrations.AddField(
            model_name="snlplayer",
            name="player_no",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
