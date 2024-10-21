
# pongapi2d/serializers.py

#########################################################################################################

from rest_framework import serializers
from .models import Pong2dGame, Pong2dAIGame

#########################################################################################################

class Pong2dGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pong2dGame
        fields = '__all__'

#########################################################################################################

class Pong2dAIGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pong2dAIGame
        fields = '__all__'

#########################################################################################################

