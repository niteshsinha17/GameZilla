from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
import time
from django.db.models import Q
import random
from game.models import Room

# Create your models here.


class TAC(models.Model):
    room = models.OneToOneField(Room, on_delete=CASCADE)
    game_id = models.SlugField()
    started = models.BooleanField(default=False)
    max_player = models.IntegerField(default=0)
    current_player = models.ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    board = JSONField(default=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    current = models.IntegerField(null=True, blank=True)
    players_entered = models.IntegerField(default=0)
    time_stamp = models.FloatField(null=True, blank=True)
    round = models.IntegerField(null=True, blank=True)
    zero = models.ForeignKey(User, related_name="zero", on_delete=CASCADE)
    cross = models.ForeignKey(User, related_name="cross", on_delete=CASCADE)
    zero_active = models.BooleanField(default=False)
    zero_entered = models.BooleanField(default=False)
    cross_active = models.BooleanField(default=False)
    cross_entered = models.BooleanField(default=False)
    winning_chances = models.IntegerField(default=8)

    def __str__(self):
        return self.game_id

    def start(self):
        self.started = True
        self.round = 0
        self.time_stamp = time.time()
        self.save()

    def get_new_state(self):
        return {
            "current_player": self.current_player.username,
            "time": 12,
            "round": self.round,
        }

    def get_state(self):
        return {
            "current_player": self.current_player.username,
            "time": 12 - int(time.time() - self.time_stamp),
            "round": self.round,
        }

    def match_state(self, state):
        return (time.time() - self.time_stamp > 12) and (state["round"] == self.round)

    def check_win(self):
        win = False
        msg = {}
        chances = self.winning_chances
        for i in range(3):
            x_count = self.board[i].count("X")
            z_count = self.board[i].count("Z")
            if x_count == 3 or z_count == 3:
                win = True
                msg = {
                    "action": "game_over",
                    "horizontal": True,
                    "position": i,
                    "tilt": False,
                }
                break
            elif x_count > 0 and z_count > 0:
                chances -= 1
        if win:
            msg["win"] = win
            return msg

        board2 = [
            [self.board[0][i], self.board[1][i], self.board[2][i]] for i in range(3)
        ]
        for i in range(3):
            x_count = board2[i].count("X")
            z_count = board2[i].count("Z")

            if x_count == 3 or z_count == 3:
                win = True
                msg = {
                    "action": "game_over",
                    "horizontal": False,
                    "position": i,
                    "tilt": False,
                }
                break
            elif x_count > 0 and z_count > 0:
                chances -= 1
        if win:
            msg["win"] = win
            return msg
        board3 = [self.board[i][i] for i in range(3)]
        x_count = board3.count("X")
        z_count = board3.count("Z")
        if x_count == 3 or z_count == 3:
            win = True
            msg = {
                "action": "game_over",
                "horizontal": False,
                "position": 0,
                "tilt": True,
            }
        elif x_count > 0 and z_count > 0:
            chances -= 1
        if win:
            msg["win"] = win
            return msg
        board4 = [self.board[2][0], self.board[1][1], self.board[0][2]]
        x_count = board4.count("X")
        z_count = board4.count("Z")
        if x_count == 3 or z_count == 3:
            win = True
            msg = {
                "action": "game_over",
                "horizontal": False,
                "position": 2,
                "tilt": True,
            }
        elif x_count > 0 and z_count > 0:
            chances -= 1
        if win:
            msg["win"] = win
            return msg

        if chances == 0:
            return {"win": win, "action": "game_over"}
        else:
            return {"action": "mark", "win": win}


class TACMessage(models.Model):
    game = models.ForeignKey(TAC, on_delete=models.CASCADE, related_name="message")
    user = models.ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    text = models.TextField()

    def __str__(self):
        return self.game.game_id + self.user.username
