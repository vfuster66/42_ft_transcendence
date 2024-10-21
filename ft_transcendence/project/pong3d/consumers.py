
# pong3d/consumers.py

#########################################################################################################

from channels.generic.websocket import AsyncWebsocketConsumer
import json

#########################################################################################################

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("game", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("game", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            "game",
            {
                'type': 'game_message',
                'message': message
            }
        )

    async def game_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

#########################################################################################################