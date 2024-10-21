
# users/apps.py

#########################################################################################################

from django.apps import AppConfig
from django.db import models

#########################################################################################################

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals

#########################################################################################################

