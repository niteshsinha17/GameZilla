from django.db import models
# from account.models import User
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
# Create your models here.


class Game(models.Model):
    game_name = models.CharField(max_length=60)
    img = models.ImageField(upload_to='images/', blank=True, null=True)
    code = models.CharField(max_length=20, null=True, blank=True)
    max_player = models.IntegerField(null=True, blank=True)
    min_player = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.game_name


class Room(models.Model):
    sp_id = models.SlugField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, default=None)
    time = models.TimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE)
    max_members = models.IntegerField(null=True, blank=True)
    members_joined = models.IntegerField(default=0)
    can_start = models.BooleanField(default=False)
    started = models.BooleanField(default=False)
    members_ready = models.IntegerField(default=1)
    game_url = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.sp_id


class Member(models.Model):
    room = models.ForeignKey(Room, on_delete=CASCADE,
                             null=True, blank=True)
    member = models.ForeignKey(User, on_delete=CASCADE)
    ready = models.BooleanField(default=False)
    host = models.BooleanField(default=False)
    room = models.ForeignKey(Room, on_delete=CASCADE, blank=True, null=True)
    in_game = models.BooleanField(default=False)
    entered = models.BooleanField(default=False)
    leaved = models.BooleanField(default=False)
    online = models.BooleanField(default=True)

    def __str__(self):
        return self.member.username
