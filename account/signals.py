from django.contrib.auth.models import User
from .models import ProfileModel
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    if created:
        ProfileModel.objects.create(user=instance)


@receiver(post_save,sender=User)
def save_profile(sender,instance,**kwargs):
    instance.Profile.save()