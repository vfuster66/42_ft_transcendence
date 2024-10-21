
# chat/consumers.py

#########################################################################################################

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from .models import Room, Message, Block, GameInvitation
import json
import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#########################################################################################################

User = get_user_model()

#########################################################################################################

logger = logging.getLogger(__name__)

#########################################################################################################

@database_sync_to_async
def get_system_user():
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='system_user',
        defaults={'is_staff': False, 'is_superuser': False}
    )
    return user

#########################################################################################################

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import threading

logger = logging.getLogger(__name__)

class GlobalChatConsumer(AsyncWebsocketConsumer):
    """
    Ce consommateur gère la connexion WebSocket pour un chat global. Il permet de connecter,
    recevoir des messages de, et déconnecter les utilisateurs de leurs groupes personnels.
    """
        
    async def connect(self):
        """
        Ce gestionnaire est appelé lorsqu'un utilisateur tente de se connecter au WebSocket.
        Il ajoute l'utilisateur à son groupe personnel et accepte la connexion WebSocket.
        """
        self.user_group_name = f"user_{self.scope['user'].id}"
        logger.info(f"Attempting to connect user {self.scope['user'].username} to their personal group {self.user_group_name}")

        try:
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.accept()
            # Lancer le keep-alive
            self.keep_alive()
            logger.info(f"User {self.scope['user'].username} successfully connected to {self.user_group_name}")
        except Exception as e:
            logger.error(f"Failed to connect user {self.scope['user'].username} to WebSocket due to {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        """
        Ce gestionnaire est appelé lorsqu'un utilisateur se déconnecte du WebSocket.
        Il retire l'utilisateur de son groupe personnel.
        """
        logger.info(f"User {self.scope['user'].username} is disconnecting from WebSocket with close code {close_code}")
        try:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            logger.info(f"User {self.scope['user'].username} successfully removed from their personal group {self.user_group_name}")
        except Exception as e:
            logger.error(f"Failed to disconnect user {self.scope['user'].username} from WebSocket due to {str(e)}")

    async def receive(self, text_data=None, bytes_data=None):
        """
        Ce gestionnaire est appelé lorsqu'un message est reçu via le WebSocket.
        """
        logger.debug(f"Received message from user {self.scope['user'].username}: {text_data if text_data else bytes_data}")

        try:
            data = text_data if text_data else bytes_data.decode()
            message = json.loads(data)
            logger.info(f"Processing message from {self.scope['user'].username}: {message}")

            # Traitement de message ici...
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing message from {self.scope['user'].username}: {str(e)}")
            await self.send(text_data=json.dumps({"error": "Error processing your message"}))

    def keep_alive(self):
        """
        Envoie des messages de keep-alive pour maintenir la connexion WebSocket ouverte.
        """
        def send_keep_alive():
            try:
                async_to_sync(self.send)(text_data=json.dumps({"type": "keep_alive"}))
                logger.debug("Keep-alive message sent")
            except Exception as e:
                logger.error(f"Keep-alive error: {str(e)}")
                return

            # Planifie l'appel suivant du keep-alive
            threading.Timer(30, send_keep_alive).start()

        # Démarre le premier appel du keep-alive
        send_keep_alive()

    async def send_tournament_notification(self, event):
        """
        Envoie une notification de tournoi à l'utilisateur via le WebSocket.
        """
        tournament_id = event['tournament_id']
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'type': 'tournament_notification',
            'tournament_id': tournament_id,
            'message': message
        }))


#########################################################################################################

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecte l'utilisateur à la fois à son groupe personnel et au groupe de la salle de chat spécifiée.
        """
        self.user_group_name = f"user_{self.scope['user'].id}"
        self.room_group_name = f"chat_{self.scope['url_route']['kwargs']['room_name']}"

        logger.info(f"User {self.scope['user'].username} attempting to connect to room {self.room_group_name} and personal group {self.user_group_name}")

        try:
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            logger.info(f"User {self.scope['user'].username} added to personal group {self.user_group_name}")
        except Exception as e:
            logger.error(f"Failed to add {self.scope['user'].username} to personal group {self.user_group_name}: {str(e)}")

        room = await self.get_room(self.scope['url_route']['kwargs']['room_name'])
        if room and await self.is_member(room, self.scope['user']):
            try:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(f"User {self.scope['user'].username} added to room group {self.room_group_name}")
            except Exception as e:
                logger.error(f"Failed to add {self.scope['user'].username} to room group {self.room_group_name}: {str(e)}")
        else:
            logger.warning(f"User {self.scope['user'].username} is not a member of room {self.room_group_name} or room does not exist")

        await self.accept()
        logger.info(f"WebSocket connection accepted for user {self.scope['user'].username}")


    async def disconnect(self, close_code):
        """
        Déconnecte l'utilisateur de son groupe personnel et du groupe de la salle de chat.
        """
        logger.info(f"User {self.scope['user'].username} disconnecting with close code {close_code}")
        try:
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
            logger.info(f"User {self.scope['user'].username} removed from personal group {self.user_group_name}")
        except Exception as e:
            logger.error(f"Failed to discard {self.scope['user'].username} from personal group {self.user_group_name}: {str(e)}")

        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            logger.info(f"User {self.scope['user'].username} removed from room group {self.room_group_name}")
        except Exception as e:
            logger.error(f"Failed to discard {self.scope['user'].username} from room group {self.room_group_name}: {str(e)}")


    @database_sync_to_async
    def is_blocked(self, sender, receiver, room_name):
        """
        Vérifie si l'expéditeur est bloqué par le destinataire dans la salle spécifiée.
        """
        logger.debug(f"is_blocked -> Checking if {sender.username} is blocked by {receiver.username} in room {room_name}")
        is_blocked = Block.objects.filter(blocker=receiver, blocked=sender, room__name=room_name).exists()
        logger.debug(f"is_blocked -> Block status for {sender.username} by {receiver.username} in room {room_name}: {is_blocked}")
        return is_blocked

    @database_sync_to_async
    def get_room(self, room_name):
        """
        Récupère une salle par son nom.
        """
        try:
            return Room.objects.get(name=room_name)
        except Room.DoesNotExist:
            logger.error(f"get_room -> Room {room_name} does not exist")
            return None

    @database_sync_to_async
    def get_user_by_username(self, username):
        """
        Récupère un utilisateur par son nom d'utilisateur.
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error(f"get_user_by_username -> User {username} does not exist")
            return None

    @database_sync_to_async
    def block_user(self, blocker, blocked_username, room_name):
        """
        Bloque un utilisateur spécifié dans une salle donnée, empêchant la communication
        entre le bloqueur et l'utilisateur bloqué.
        """
        try:
            blocked = User.objects.get(username=blocked_username)
            room = Room.objects.get(name=room_name)

            existing_block = Block.objects.filter(blocker=blocker, blocked=blocked, room=room).exists()
            if not existing_block:
                Block.objects.create(blocker=blocker, blocked=blocked, room=room)
                logger.info(f"block_user -> User {blocked_username} successfully blocked by {blocker.username} in room {room_name}")
                return True
            else:
                logger.info(f"block_user -> Block already exists between {blocker.username} and {blocked_username} in room {room_name}")
                return False
        except (User.DoesNotExist, Room.DoesNotExist):
            logger.error(f"block_user -> User {blocked_username} or Room {room_name} not found for blocking by {blocker.username}")
            return False
        except Exception as e:
            logger.error(f"block_user -> Failed to block user {blocked_username} by {blocker.username} in room {room_name}: {str(e)}")
            return False

    @database_sync_to_async
    def unblock_user(self, blocker, blocked_username, room_name):
        """
        Débloque un utilisateur spécifié, permettant à nouveau la communication dans la salle spécifiée.
        """
        logger.debug(f"Tentative de déblocage de l'utilisateur {blocked_username} par {blocker.username} dans la salle {room_name}")
        try:
            blocked = User.objects.get(username=blocked_username)
            room = Room.objects.get(name=room_name)

            block_count, _ = Block.objects.filter(blocker=blocker, blocked=blocked, room=room).delete()
            if block_count > 0:
                logger.info(f"L'utilisateur {blocked_username} a été débloqué avec succès par {blocker.username} dans la salle {room_name}")
                return True
            else:
                logger.warning(f"Aucun blocage trouvé entre {blocker.username} et {blocked_username} à supprimer dans la salle {room_name}")
                return False
        except (User.DoesNotExist, Room.DoesNotExist):
            logger.error(f"L'utilisateur {blocked_username} ou la salle {room_name} n'a pas été trouvé pour un déblocage par {blocker.username}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors du déblocage de l'utilisateur {blocked_username} par {blocker.username} dans la salle {room_name}: {str(e)}")
            return False


    async def receive(self, text_data):
        logger.debug(f"Receiving new message: {text_data}")
        data = json.loads(text_data)
        message = data.get('message', '')
        room_name = data.get('room_name')
        username = data.get('username')
        command = data.get('command')

        logger.debug(f"Message parsed as: {data}")

        if not room_name or not await self.get_room(room_name):
            logger.warning(f"receive -> Invalid room: {room_name}")
            await self.send_error("receive -> Salle non spécifiée ou inexistante.")
            return

        sender = self.scope['user']
        logger.info(f"receive -> Message from {sender.username} in room {room_name} with command {command}")

        if command:
            logger.debug(f"receive -> Command found: {command}")
            await self.handle_command(command, username, room_name, sender, data)
        else:
            logger.debug("receive -> No command found, processing message")
            await self.process_message(sender, room_name, message, data)


    async def handle_command(self, command, username, room_name, sender, data):
        """
        Gère diverses commandes reçues via WebSocket,
        telles que inviter, retirer, bloquer, débloquer un utilisateur, et gérer les invitations de jeu.
        """
        message_type = data.get('type')
        
        logger.debug(f"handle_command -> Handling command: {command} for user: {username} in room: {room_name}")
        if command:
            if command == 'invite':
                await self.invite_user(username, room_name, sender)
            elif command == 'remove_member':
                await self.remove_member(username, room_name)
            elif command == 'block_user':
                await self.block_user(sender, username, room_name)
            elif command == 'unblock_user':
                await self.unblock_user(sender, username, room_name)
            elif command == 'invite_to_game':
                game = data.get('game')  # Assurez-vous que 'game' est bien présent dans 'data'
                await self.handle_game_invite(username, room_name, sender, game)
            elif command == 'accept_game_invite':
                invitation_id = data.get('invitation_id')
                if invitation_id:
                    await self.accept_game_invitation(invitation_id)
                else:
                    await self.send_error("ID d'invitation manquant pour accepter l'invitation au jeu.")
            elif command == 'decline_game_invite':
                invitation_id = data.get('invitation_id')
                if invitation_id:
                    await self.decline_game_invitation(invitation_id)
                else:
                    await self.send_error("ID d'invitation manquant pour décliner l'invitation au jeu.")
            else:
                logger.error(f"Unknown command: {command}")
                await self.send_error("Commande non reconnue ou données insuffisantes fournies.")
        elif message_type == 'game_invite':
            await self.game_invite(data)



    async def process_message(self, sender, room_name, message, data):
        """
        Traite un message de chat, en vérifiant d'abord si le destinataire a bloqué l'expéditeur.
        """
        receiver_username = data.get('receiver_username')
        if receiver_username:
            receiver = await self.get_user_by_username(receiver_username)
            if not receiver or await self.is_blocked(sender, receiver, room_name):
                await self.send_error("Vous ne pouvez pas envoyer de messages à cet utilisateur.")
                return
        await self.store_message(room_name, sender, message)
        await self.broadcast_message_to_room(room_name, sender, message)


    async def broadcast_message_to_room(self, room_name, sender, message):
        """
        Diffuse un message à tous les membres de la salle qui n'ont pas bloqué l'expéditeur.
        """
        room = await self.get_room(room_name)
        if not room:
            logger.error(f"La salle {room_name} n'a pas pu être récupérée pour la diffusion du message.")
            return

        members = await database_sync_to_async(list)(room.members.all())

        for member in members:
            local_time = timezone.localtime(timezone.now())
            if not await self.is_blocked(sender, member, room_name):
                await self.channel_layer.group_send(
                    f"user_{member.id}",
                    {
                        "type": "chat_message",
                        "message": message,
                        "username": sender.username,
                        "timestamp": local_time.strftime("%H:%M")
                    }
                )
            else:
                logger.info(f"Le message de {sender.username} à {member.username} a été bloqué dans la salle {room_name}.")

# admission dans une salle de chat

    async def invite_user(self, username, room_name, sender):
        """
        Invite un utilisateur à rejoindre une salle, en vérifiant si l'expéditeur est membre
        de cette salle et que l'invité n'en est pas déjà membre. Ajoute ensuite l'invité à la salle.
        """
        if not username:
            await self.send_error("Nom d'utilisateur du destinataire manquant pour l'invitation.")
            return

        room = await self.get_room(room_name)
        invitee = await self.get_user_by_username(username)

        if not room or not invitee:
            await self.send_error("Salle ou utilisateur à inviter introuvable.")
            return

        sender_is_member = await self.is_member(room, sender)
        invitee_is_member = await self.is_member(room, invitee)

        if sender_is_member and not invitee_is_member:
            if await self.add_user_to_room(room, invitee):
                await self.send_info(f"{username} a été ajouté et invité à la salle {room_name}.")
            else:
                await self.send_error("Échec de l'ajout de l'utilisateur à la salle.")
        else:
            if not sender_is_member:
                await self.send_error("L'expéditeur n'est pas autorisé à inviter des utilisateurs dans cette salle.")
            elif invitee_is_member:
                await self.send_error("L'utilisateur est déjà membre de la salle.")


    async def remove_member(self, username, room_name):
        """
        Retire un utilisateur de la salle si l'utilisateur spécifié est actuellement membre de la salle.
        """
        room = await self.get_room(room_name)
        if room is None:
            await self.send_error("Salle non trouvée.")
            return

        user_to_remove = await self.get_user_by_username(username)
        if user_to_remove is None:
            await self.send_error("Utilisateur non trouvé.")
            return

        is_member = await database_sync_to_async(room.is_member)(user_to_remove)
        if is_member:
            await database_sync_to_async(room.remove_member)(user_to_remove)
            await self.send_info(f"{username} a été retiré de la salle {room_name}.")
        else:
            await self.send_error("L'utilisateur n'est pas membre de la salle.")


    async def send_info(self, message):
        await self.send(text_data=json.dumps({
            "type": "info",
            "message": message
        }))


    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": message
        }))


    @database_sync_to_async
    def check_member(self, room, user):
        """
        Vérifie si un utilisateur est membre d'une salle donnée.
        """
        is_member = room.is_member(user)
        logger.debug(f"Checking membership: User {user.username} membership status in {room.name} is {is_member}")
        return is_member


    async def invite_to_room(self, room_name, username_to_invite):
        """
        Tente d'inviter un utilisateur à une salle. Assure que l'inviteur est autorisé à envoyer des invitations.
        """
        logger.info(f"{self.scope['user'].username} is attempting to invite {username_to_invite} to room {room_name}")

        room = await self.get_room(room_name)
        inviter = self.scope["user"]
        invitee = await self.get_user_by_username(username_to_invite)

        if not room:
            logger.error(f"Room {room_name} not found; invitation from {inviter.username} to {username_to_invite} cannot proceed.")
            return False

        if not invitee:
            logger.error(f"User {username_to_invite} not found; cannot invite non-existent user.")
            return False

        if not await self.is_member(room, inviter):
            logger.error(f"{inviter.username} is not authorized to invite others to room {room_name}.")
            return False

        if await self.is_member(room, invitee):
            logger.info(f"{invitee.username} is already a member of {room_name}.")
            return True

        if await self.add_user_to_room(room, invitee):
            logger.info(f"{invitee.username} added to room {room_name} by {inviter.username}")
            return True
        else:
            logger.error(f"Failed to add {invitee.username} to {room_name}")
            return False


    @database_sync_to_async
    def add_user_to_room(self, room, user):
        """
        Ajoute un utilisateur à la salle après une invitation réussie.
        """
        try:
            room.members.add(user)
            room.save()
            logger.info(f"User {user.username} successfully added to room {room.name}.")
            return True
        except Exception as e:
            logger.error(f"Error adding user {user.username} to room {room.name}: {str(e)}")
            return False


    async def user_kicked(self, event):
        """
        Notifie l'utilisateur qu'il a été expulsé de la salle, généralement appelé par un événement du groupe.
        """
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'user_kicked',
            'message': message
        }))
        await self.close() 
        logger.info(f"Sent kick message to client: {message}")


    @database_sync_to_async
    def remove_member_from_room(self, room_name, username_to_remove):
        """
        Supprime un utilisateur de la salle s'il en est actuellement membre.
        """
        logger.info(f"Attempting to remove {username_to_remove} from {room_name}")
        try:
            room = Room.objects.get(name=room_name)
            user_to_remove = User.objects.get(username=username_to_remove)
            if user_to_remove and room:
                if user_to_remove in room.members.all():
                    room.members.remove(user_to_remove)
                    room.save()
                    logger.info(f"{username_to_remove} removed from {room_name}")
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{user_to_remove.id}",
                        {
                            "type": "user_kicked",
                            "message": f"You have been removed from {room_name}"
                        }
                    )
                    return True, "User removed successfully"
                else:
                    return False, "User is not a member of the room"
        except Room.DoesNotExist:
            logger.error(f"Room {room_name} not found.")
            return False, "Room not found"
        except User.DoesNotExist:
            logger.error(f"User {username_to_remove} not found.")
            return False, "User not found"


    async def handle_remove_member(self, room_name, username_to_remove):
        """
        Gère l'action de suppression d'un membre de la salle, vérifie si l'action a réussi
        et envoie une notification appropriée.
        """
        success, message = await self.remove_member_from_room(room_name, username_to_remove)
        if success:
            await self.send(text_data=json.dumps({
                'type': 'info',
                'message': message
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': message
            }))


    @database_sync_to_async
    def is_room_private(self, room_name):
        """
        Détermine si une salle est privée.
        """
        result = Room.objects.filter(name=room_name, is_private=True).exists()
        logger.debug(f"Room {room_name} private: {result}")
        return result


    @database_sync_to_async
    def is_member(self, room_name, user):
        """
        Vérifie si un utilisateur est membre d'une salle donnée.
        """
        try:
            room = Room.objects.get(name=room_name)
            is_member = room.members.filter(id=user.id).exists()
            logger.debug(f"User {user.username} membership status in {room_name}: {is_member}")
            return is_member
        except Room.DoesNotExist:
            logger.error(f"Room {room_name} does not exist")
            return False


    async def store_message(self, room_name, user, message, receiver_username=None):
        """
        Stocke un message dans la base de données après avoir vérifié que le destinataire
        est membre de la salle et n'a pas bloqué l'expéditeur.
        """
        logger.info(f"Attempting to retrieve room: {room_name}")
        try:
            room = await database_sync_to_async(Room.objects.get)(name=room_name)
            logger.info(f"Room {room_name} retrieved successfully.")
        except Room.DoesNotExist:
            logger.error(f"Room {room_name} not found.")
            return
        
        if not message:
            logger.warning("Empty message received, ignoring...")
            return

        receiver = None
        if receiver_username:
            logger.info(f"Looking up user: {receiver_username}")
            try:
                receiver = await database_sync_to_async(User.objects.get)(username=receiver_username)
                logger.info(f"User {receiver_username} found.")
            except User.DoesNotExist:
                logger.error(f"User {receiver_username} does not exist.")
                return
            
            if not await database_sync_to_async(room.is_member)(receiver):
                logger.error(f"Attempt to send direct message to non-member {receiver.username} in room {room_name}")
                return
        else:
            logger.info("No receiver specified, using system user.")
            receiver = await get_system_user()
            logger.info(f"System user {receiver.username} assigned as receiver.")
        
        logger.info(f"Creating message in room {room_name} from {user.username} to {receiver.username}")
        await database_sync_to_async(Message.objects.create)(
            sender=user,
            receiver=receiver,
            room=room,
            content=message
        )
        logger.info("Message created successfully.")


    @database_sync_to_async
    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} does not exist")
            return None

    async def chat_message(self, event):
        """
        Gère l'envoi de messages de chat aux clients WebSocket, formatant les données en conséquence.
        """
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))


    @database_sync_to_async
    def create_game_invitation(self, inviter, invitee_username, room_name, game):
        logger.debug(f"Creating game invitation for {invitee_username} in room {room_name} for game {game}")
        invitee = User.objects.get(username=invitee_username)
        room = Room.objects.get(name=room_name)
        invitation = GameInvitation.objects.create(inviter=inviter, invitee=invitee, room=room, game=game)
        logger.debug(f"Game invitation created with ID {invitation.id}: {invitation}")
        return invitation


    async def handle_game_invite(self, username, room_name, sender, game):
        logger.debug(f"handle_game_invite appelé avec les paramètres - username: {username}, room_name: {room_name}, sender: {sender.username}, game: {game}")
        
        try:
            logger.debug(f"Récupération de l'utilisateur à inviter : {username}")
            invitee = await database_sync_to_async(User.objects.get)(username=username)
            logger.debug(f"Utilisateur récupéré avec succès : {invitee.username}")
            
            logger.debug(f"Création de l'invitation de jeu pour {username} dans la salle {room_name} pour le jeu {game}")
            invitation = await self.create_game_invitation(sender, invitee.username, room_name, game)
            logger.debug(f"Invitation de jeu créée avec succès avec ID {invitation.id} pour le jeu {game}")
            
            message_data = {
                "type": "game_invite",
                "message": f"You have been invited to play {game.replace('_', ' ')} in {room_name} by {sender.username}",
                "inviter": sender.username,
                "room": room_name,
                "game": game,
                "invitation_id": invitation.id
            }

            logger.debug(f"Envoi de l'invitation de jeu avec les données : {message_data}")
            await self.channel_layer.group_send(
                f"user_{invitee.id}",
                {
                    "type": "game_invite",
                    "message": message_data['message'],
                    "inviter": message_data['inviter'],
                    "room": message_data['room'],
                    "game": message_data['game'],
                    "invitation_id": message_data['invitation_id']
                }
            )
            logger.debug(f"Invitation de jeu envoyée à {invitee.username}")
        
        except User.DoesNotExist:
            logger.error(f"L'utilisateur {username} n'existe pas.")
        except Exception as e:
            logger.error(f"Erreur lors de l'invitation de jeu : {e}")


    @database_sync_to_async
    def accept_game_invitation(self, invitation_id):
        logger.debug(f"Accepting game invitation with ID: {invitation_id}")
        invitation = GameInvitation.objects.get(id=invitation_id)
        invitation.accept_invitation()
        logger.debug(f"Game invitation accepted: {invitation}")
        return invitation

    @database_sync_to_async
    def decline_game_invitation(self, invitation_id):
        logger.debug(f"Declining game invitation with ID: {invitation_id}")
        invitation = GameInvitation.objects.get(id=invitation_id)
        invitation.decline_invitation()
        logger.debug(f"Game invitation declined: {invitation}")
        return invitation

    async def send_invitation_status(self, inviter_id, status, game, invitee, room_name):
        """
        Envoie un message WebSocket à l'utilisateur invitant pour l'informer du statut de l'invitation.
        """
        logger.debug(f"Sending invitation status to inviter (ID: {inviter_id}): {status}")
        await self.channel_layer.group_send(
            f"user_{inviter_id}",
            {
                "type": "invitation_status",
                "status": status,
                "game": game,
                "invitee": invitee,
                "room": room_name
            }
        )

    async def receive_json(self, content):
        logger.debug(f"Received JSON data: {content}")
        command = content.get('command')

        if command == 'invite_to_game':
            username = content['username']
            game = content['game']
            await self.handle_game_invite(username, self.room_group_name, self.scope['user'], game)
        elif command == 'accept_game_invite':
            invitation_id = content.get('invitation_id')
            if invitation_id:
                invitation = await self.accept_game_invitation(invitation_id)
                await self.send_invitation_status(invitation.inviter.id, "accepted", invitation.game, invitation.invitee.username, invitation.room.name)
            else:
                await self.send_error("ID d'invitation manquant pour accepter l'invitation au jeu.")
        elif command == 'decline_game_invite':
            invitation_id = content.get('invitation_id')
            if invitation_id:
                invitation = await self.decline_game_invitation(invitation_id)
                await self.send_invitation_status(invitation.inviter.id, "declined", invitation.game, invitation.invitee.username, invitation.room.name)
            else:
                await self.send_error("ID d'invitation manquant pour décliner l'invitation au jeu.")
        elif command == 'block_user':
            username = content.get('username')
            room_name = content.get('room_name')
            logger.debug(f"Handling command: block_user for user: {username} in room: {room_name}")
            await self.block_user(username, room_name, self.scope['user'])
        else:
            logger.error(f"Unknown command: {command}")
            await self.send_error("Commande non reconnue ou données insuffisantes fournies.")

    async def invitation_status(self, event):
        """
        Envoie une notification à l'inviteur sur le statut de l'invitation.
        """
        status = event['status']
        game = event['game']
        invitee = event['invitee']
        room = event['room']

        await self.send(text_data=json.dumps({
            'type': 'invitation_status',
            'status': status,
            'game': game,
            'invitee': invitee,
            'room': room
        }))



    async def game_invite(self, event):
        """
        Gère l'envoi d'une invitation à jouer à un client WebSocket.
        """
        logger.debug("Received game invitation event")
        message = event['message']
        inviter = event['inviter']
        room = event['room']
        game = event['game']  # Assurez-vous que le champ game est inclus
        invitation_id = event.get('invitation_id')
        logger.debug(f"Invitation ID: {invitation_id}, Game: {game}")
        await self.send(text_data=json.dumps({
            'type': 'game_invite',
            'message': message,
            'inviter': inviter,
            'room': room,
            'game': game,  # Ajoutez le champ game ici
            'invitation_id': invitation_id
        }))

#########################################################################################################
