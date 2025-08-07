from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile_and_token(sender, instance, created, **kwargs):
    if created:
        # Create a Profile instance for the new user
        Profile.objects.create(user=instance)
        # Create an authentication token for the new user
        Token.objects.create(user=instance)
