from django.db import models
# from account.models import User
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
import string
from django.utils.text import slugify
import random
# Create your models here.


class Game(models.Model):
    game_name = models.CharField(max_length=60)
    img = models.ImageField(upload_to='images/', blank=True, null=True)
    code = models.CharField(max_length=20, null=True, blank=True)
    max_player = models.IntegerField(null=True, blank=True)
    min_player = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.game_name


class RoomManager(models.Manager):
    def get_hosted_rooms(self, user):
        return self.filter(created_by=user)

    def can_create_room(self, user):
        return self.filter(created_by=user).count() < 3


class MemberManager(models.Manager):
    def get_joined_rooms(self, user):
        print(user.username)
        return [member.room for member in
                self.filter(member=user, host=False, leaved=False)]


class Room(models.Model):
    sp_id = models.SlugField(blank=True, null=True, max_length=254)
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
    objects = RoomManager()

    def __str__(self):
        return self.sp_id

    def save(self, *args, **kwargs):
        super(Room, self).save(*args, **kwargs)

    def get_state(self):
        return {
            'game_code': self.game.code,
            'max_members': self.max_members,
            'members_joined': self.members_joined,
            'members_ready': self.members_ready,
            'room_no': self.sp_id
        }

    def reset(self):
        self.members_ready = 1
        self.started = False
        self.game_url = ''
        members = Member.objects.filter(room=self)
        for member in members:
            if member.leaved and not member.host:
                member.delete()
                continue
            if not member.host:
                member.ready = False
            elif member.leaved:
                # host who has leaved
                member.leaved = False
            member.online = False
            member.save()
        self.save()


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
    objects = MemberManager()

    def __str__(self):
        return self.member.username + self.room.sp_id


class Report(models.Model):
    reported_by = models.ForeignKey(User, on_delete=CASCADE)
    game = models.ForeignKey(Game, on_delete=CASCADE)
    discription = models.TextField()
    spotted = models.BooleanField(default=False)
    solved = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.created_by.username)
    Klass = instance.__class__
    slug_exit = Klass.objects.filter(sp_id=slug).exists()

    if slug_exit:
        new_slug = "{slug}-{randstr}".format(
            slug=slug, randstr=random_string_generator(size=4))
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.sp_id:
        instance.sp_id = unique_slug_generator(instance)


pre_save.connect(pre_save_receiver, sender=Room)
