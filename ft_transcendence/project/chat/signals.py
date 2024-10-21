
# chat/signals.py

#########################################################################################################

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Room, GameInvitation

#########################################################################################################

User = get_user_model()

#########################################################################################################

@receiver(post_save, sender=User)
def add_user_to_public_rooms(sender, instance, created, **kwargs):
    if created:
        public_rooms = Room.objects.filter(is_private=False)
        for room in public_rooms:
            room.members.add(instance)

@receiver(post_save, sender=Room)
def add_all_users_to_public_room(sender, instance, created, **kwargs):
    if created and not instance.is_private:
        all_users = User.objects.all()
        instance.members.add(*all_users)

@receiver(post_save, sender=GameInvitation)
def post_invitation_save(sender, instance, created, **kwargs):
    if instance.accepted:
        # Envoyer une notification ou démarrer le jeu
        print(f"Notification: Game between {instance.inviter.username} and {instance.invitee.username} in {instance.room.name} can start.")
    
#########################################################################################################