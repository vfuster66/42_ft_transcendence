
# pong3d/serializers.py

#########################################################################################################

from rest_framework import serializers
from users.models import Game

#########################################################################################################

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['player1', 'player2', 'winner', 'player1_score', 'player2_score', 'completed']

#########################################################################################################