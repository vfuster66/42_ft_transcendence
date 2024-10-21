
# chat/serializers.py

#########################################################################################################
from rest_framework import serializers
from .models import Message

#########################################################################################################

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'room', 'sender', 'receiver']

    def validate_content(self, value):
        if not value:
            raise serializers.ValidationError("Le contenu du message ne peut pas être vide.")
        return value

#########################################################################################################