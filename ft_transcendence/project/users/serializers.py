
# users/serializers.py

#########################################################################################################

from django.contrib.auth.models import User

from rest_framework import serializers

from .models import UserProfile, UserProfile, Game

#########################################################################################################

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['user', 'avatar_url']

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return request.build_absolute_uri('/static/images/avatars/avatar_0.png')

#########################################################################################################

class UserSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    avatar_url = serializers.ImageField(source='profile.avatar')

    class Meta:
        model = UserProfile
        fields = ['user', 'avatar_url']

#########################################################################################################

class GameSerializer(serializers.ModelSerializer):
    player1 = serializers.CharField(source='player1.username')
    player2 = serializers.CharField(source='player2.username')
    winner = serializers.CharField(source='winner.username', required=False, allow_null=True)

    class Meta:
        model = Game
        fields = ['player1', 'player2', 'player1_score', 'player2_score', 'winner', 'game_date']

#########################################################################################################



