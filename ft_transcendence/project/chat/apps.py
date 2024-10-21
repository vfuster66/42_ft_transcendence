
# chat/apps.py

#########################################################################################################

from django.apps import AppConfig

#########################################################################################################

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        # S'assure que l'application est prête avant d'importer les signaux
        from . import signals

#########################################################################################################