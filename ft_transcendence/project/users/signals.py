
# signals.py

#########################################################################################################

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import UserProfile, Game

#########################################################################################################

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, display_name=instance.username)
    else:
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance, display_name=instance.username)
        instance.profile.save()

    profile = instance.profile
    profile.first_name = instance.first_name
    profile.last_name = instance.last_name
    profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(user_logged_in)
def user_logged_in(sender, request, user, **kwargs):
    if hasattr(user, 'profile'):
        user.profile.status = 'ONLINE'
        user.profile.save()


@receiver(user_logged_out)
def user_logged_out(sender, request, user, **kwargs):
    if hasattr(user, 'profile'):
        user.profile.status = 'OFFLINE'


@receiver(post_save, sender=Game)
def update_user_statistics(sender, instance, **kwargs):
    # Assuming you want to update statistics for both players
    if instance.completed:
        if instance.player1:
            profile1 = instance.player1.profile
            profile1.total_wins += 1 if instance.winner == instance.player1 else 0
            profile1.total_losses += 1 if instance.winner != instance.player1 else 0
            profile1.save()

        if instance.player2:
            profile2 = instance.player2.profile
            profile2.total_wins += 1 if instance.winner == instance.player2 else 0
            profile2.total_losses += 1 if instance.winner != instance.player2 else 0
            profile2.save()

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_ai_user(sender, **kwargs):
    if not User.objects.filter(username='AI').exists():
        User.objects.create_user(username='AI', password='ai_password', email='ai@example.com')
        logger.info("AI user created successfully.")
    else:
        logger.info("AI user already exists.")


#########################################################################################################

