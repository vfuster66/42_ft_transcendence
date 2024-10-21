
# chat/admin.py

#########################################################################################################

from django.contrib import admin
from .models import Message, Room

#########################################################################################################

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'room', 'timestamp')
    search_fields = ('content', 'room__name')
    list_filter = ('timestamp', 'room__name')
    date_hierarchy = 'timestamp'

#########################################################################################################

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_private', 'list_members', 'list_blocks')  # Ajouter 'list_blocks'
    search_fields = ('name',)
    list_filter = ('is_private',)

    def list_members(self, obj):
        """Renvoie une liste de noms d'utilisateurs des membres de la salle."""
        return ", ".join([user.username for user in obj.members.all()])
    list_members.short_description = "Membres"

    def list_blocks(self, obj):
        """Renvoie une liste des blocages dans la salle."""
        blocks = obj.blocks.all()
        return ", ".join([f"{block.blocker.username} blocked {block.blocked.username}" for block in blocks])
    list_blocks.short_description = "Blocages"

#########################################################################################################

admin.site.register(Message, MessageAdmin)
admin.site.register(Room, RoomAdmin)

#########################################################################################################
