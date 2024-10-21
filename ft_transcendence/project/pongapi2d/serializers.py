
# pongapi2d/serializers.py

#########################################################################################################

from rest_framework import serializers
from .models import Pongapi2dGame, Pongapi2dAIGame

#########################################################################################################

class Pongapi2dGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pongapi2dGame
        fields = '__all__'

#########################################################################################################

class Pongapi2dAIGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pongapi2dAIGame
        fields = '__all__'

#########################################################################################################

