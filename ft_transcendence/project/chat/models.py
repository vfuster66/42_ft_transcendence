
# chat/models.py

#########################################################################################################

from django.db import models
from django.contrib.auth import get_user_model
import logging
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#########################################################################################################

logger = logging.getLogger(__name__)

#########################################################################################################

User = get_user_model()

#########################################################################################################

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_private = models.BooleanField(default=False)
    members = models.ManyToManyField(User, related_name='rooms', blank=True)

    def __str__(self):
        return self.name

    def is_member(self, user):
        if not self.is_private:
            return True
        return self.members.filter(id=user.id).exists()

    def add_member(self, user):
        if not self.is_member(user):
            self.members.add(user)
            logger.debug(f"Added user {user.username} to room {self.name}")

    def remove_member(self, user):
        if self.is_member(user):
            self.members.remove(user)
            logger.debug(f"Removed user {user.username} from room {self.name}")

    def invite_user(self, user, inviter):
        if not self.is_member(user) and inviter in self.members.all():
            Invitation.objects.create(room=self, invitee=user, inviter=inviter)
            logger.debug(f"User {inviter.username} invited {user.username} to room {self.name}")

#########################################################################################################

class Message(models.Model):
    sender = models.ForeignKey('auth.User', related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey('auth.User', related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)

    def __str__(self):
        return self.content
    
#########################################################################################################

class Invitation(models.Model):
    room = models.ForeignKey(Room, related_name="invitations", on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, related_name="sent_invitations", on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, related_name="received_invitations", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation from {self.inviter.username} to {self.invitee.username} for room {self.room.name}"


    def accept(self):
        if self.status == 'pending':
            self.room.add_member(self.invitee)
            self.status = 'accepted'
            self.save()
            logger.debug(f"Invitation accepted by {self.invitee.username} for room {self.room.name}")

    def decline(self):
        if self.status == 'pending':
            self.status = 'declined'
            self.save()
            logger.debug(f"Invitation declined by {self.invitee.username} for room {self.room.name}")

#########################################################################################################

class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='blocks', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked', 'room')

    def __str__(self):
        return f"{self.blocker.username} has blocked {self.blocked.username} in {self.room.name}"
    
#########################################################################################################

class GameInvitation(models.Model):
    inviter = models.ForeignKey(User, related_name='sent_game_invitations', on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, related_name='received_game_invitations', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='game_invitations')
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    game_started = models.BooleanField(default=False)
    game = models.CharField(max_length=50)  # Assurez-vous que le champ game est présent

    def __str__(self):
        return f"Invitation from {self.inviter.username} to {self.invitee.username} for {self.game} game in room {self.room.name}"

    def accept_invitation(self):
        self.accepted = True
        self.save()
        # Logique supplémentaire pour démarrer le jeu pourrait être ajoutée ici
        print(f"Invitation accepted for game in {self.room.name} between {self.inviter.username} and {self.invitee.username}")
        self.notify_inviter("accepted")

    def decline_invitation(self):
        self.delete()  # Ou mettre à jour un champ `refused` si vous choisissez de le conserver
        print(f"Invitation declined for game in {self.room.name} by {self.invitee.username}")
        self.notify_inviter("declined")

    def notify_inviter(self, status):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{self.inviter.id}",
            {
                "type": "invitation_status",
                "status": status,
                "game": self.game,
                "invitee": self.invitee.username,
                "room": self.room.name
            }
        )

    def is_accepted(self):
        return self.accepted

    def is_game_started(self):
        return self.game_started


#########################################################################################################

