from django.db import models
from django.contrib.auth.models import User
# Create your models here.


# class User(AbstractUser):
#     guest = models.BooleanField(default=False)

#User Profile 
class Profile(models.Model):
      user=models.OneToOneField(User, on_delete=models.CASCADE,related_name="Profile")
      email=models.EmailField(max_length=254,default="None@gamezila.fun")

      def save(self,*args, **kwargs):
            return super().save(*args, **kwargs)

      def __str__(self):
          return str(self.user)
                  