from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.


# class User(AbstractUser):
#     guest = models.BooleanField(default=False)

from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES=(
       ('M',"Male"),
       ('F',"Female"),
       ('O',"Other"),
       ('P',"Prefer not to say"),
    )

    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="Profile")
    coins=models.PositiveIntegerField(default=0)
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES)
    dob=models.DateField(null=True,blank=True)
    total_play_count=models.PositiveIntegerField(default=0)
    matches_won=models.PositiveIntegerField(default=0)
    matches_draw=models.PositiveIntegerField(default=0)
    matches_lost=models.PositiveIntegerField(default=0)


    def __str__(self):
        return f'{self.user} Profile'
