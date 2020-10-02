from django.db import models
from game.models import *
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
# Create your models here.


class SNL(models.Model):
    room = models.OneToOneField(Room, on_delete=CASCADE)
    game_id = models.SlugField()
    # no use of winner
    started = models.BooleanField(default=False)
    max_player = models.IntegerField(default=0)
    current_player = models.ForeignKey(
        User, on_delete=CASCADE, null=True, blank=True)

    current = models.IntegerField(null=True, blank=True)
    winner_state = models.IntegerField(default=0)
    player_entered = models.IntegerField(default=0)
    time_stamp = models.FloatField(null=True, blank=True)
    round = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.game_id


class SNLPlayer(models.Model):
    COLORS = (('RED', 'RED'),
              ('BLUE', 'BLUE'),
              ('YELLOW', 'YELLOW'),
              ('GREEN', 'GREEN'))
    game = models.ForeignKey(SNL, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=CASCADE)
    rank = models.IntegerField(default=0)
    color = models.CharField(max_length=10, default='', choices=COLORS)

    # no use of ready
    ready = models.BooleanField(default=False)
    online = models.BooleanField(default=True)
    left = models.IntegerField(default=0)
    bottom = models.IntegerField(default=0)
    '''

    disable will tell weather player win or not

    '''
    disable = models.BooleanField(default=False)
    position = models.IntegerField(default=1)
    can_move = models.BooleanField(default=False)
    entered = models.BooleanField(default=False)

    def __str__(self):
        return self.player.username + self.game.game_id


class SNLMessage(models.Model):
    game = models.ForeignKey(SNL, on_delete=models.CASCADE)
    player = models.ForeignKey(SNLPlayer, on_delete=CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.game.game_id + self.player.user.username
