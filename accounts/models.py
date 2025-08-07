from django.db import models
from django.contrib.auth.models import User


def profile_picture_path(instance, filename):
    return f'profile_pictures/{instance.user.id}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    profile_picture = models.ImageField(
        upload_to=profile_picture_path, null=True, blank=True)

    def __str__(self):
        return self.user.username
