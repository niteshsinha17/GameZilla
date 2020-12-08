from django.db import models
from game.models import *
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
import time
from django.db.models import Q
import random
# Create your models here.


class SNL(models.Model):
    room = models.OneToOneField(Room, on_delete=CASCADE)
    game_id = models.SlugField()
    started = models.BooleanField(default=False)
    max_player = models.IntegerField(default=0)
    current_player = models.ForeignKey(
        User, on_delete=CASCADE, null=True, blank=True)
    current = models.IntegerField(null=True, blank=True)
    winner_state = models.IntegerField(default=0)
    players_playing = models.IntegerField(default=0)
    players_entered = models.IntegerField(default=0)
    players_disabled = models.IntegerField(default=0)
    time_stamp = models.FloatField(null=True, blank=True)
    round = models.IntegerField(null=True, blank=True)
    last_check = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.game_id

    def start(self):
        self.started = True
        self.round = 0
        self.time_stamp = time.time()
        self.last_check = time.time()
        self.current = random.randint(0, self.players_playing-1)
        players = self.players.filter(
            entered=True, disable=False, leaved=False)
        self.current_player = players[self.current].player
        self.save()

    def get_new_state(self):
        return {'current_player': self.current_player.username,
                "time": 12,
                "round": self.round
                }

    def get_state(self):
        return {'current_player': self.current_player.username,
                "time": 12 - int(time.time()-self.time_stamp),
                "round": self.round
                }

    def match_state(self, state):
        return ((time.time() - self.last_check) > 12) and (time.time()-self.time_stamp > 12) and state['round'] == self.round

    def get_not_joined_players(self):
        players = []
        members = Member.objects.filter(room=self.room)
        room = self.room
        for player in self.players.filter(entered=False):
            players.append({'member': player.player.username,
                            'leaved_msg': 'some players left due to network', 'leaved': True, 'was_ready': True})
            member = members.get(member=player.player)
            player.leaved = True
            member.leaved = True
            player.online = False
            if not member.host:
                room.members_joined -= 1
                room.members_ready -= 1
            member.save()
            player.save()
            room.save()
        return players


class SNLPlayer(models.Model):
    COLORS = (('RED', 'RED'),
              ('BLUE', 'BLUE'),
              ('YELLOW', 'YELLOW'),
              ('GREEN', 'GREEN'))
    member = models.OneToOneField(
        Member, null=True, blank=True, on_delete=CASCADE)
    game = models.ForeignKey(
        SNL, on_delete=CASCADE, related_name='players')
    player = models.ForeignKey(User, on_delete=CASCADE)
    rank = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=10, default='', choices=COLORS)
    online = models.BooleanField(default=True)
    player_no = models.IntegerField(null=True, blank=True)
    leaved = models.BooleanField(default=False)
    disable = models.BooleanField(default=False)
    position = models.IntegerField(default=1)
    can_move = models.BooleanField(default=False)
    entered = models.BooleanField(default=False)
    skip_chance = models.IntegerField(default=1)

    def __str__(self):
        return self.player.username + self.game.game_id

    def set_chance(self):
        if self.skip_chance == 0:
            self.skip_chance = 1
            self.save()


class SNLMessage(models.Model):
    game = models.ForeignKey(
        SNL, on_delete=models.CASCADE, related_name='message')
    user = models.ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    text = models.TextField()

    def __str__(self):
        return self.game.game_id + self.user.username
