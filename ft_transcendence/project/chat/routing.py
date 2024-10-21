
# chat/routing.py

#########################################################################################################

from django.urls import re_path
from .consumers import ChatConsumer, GlobalChatConsumer

#########################################################################################################

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/global/$', GlobalChatConsumer.as_asgi()),
]

#########################################################################################################

