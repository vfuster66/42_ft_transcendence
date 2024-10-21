
#invaders/models.py

#########################################################################################################

from django.contrib.auth.models import User
from django.db import models
from users.models import Game

#########################################################################################################

class Player(models.Model):
    username = models.CharField(max_length=100)
    high_score = models.IntegerField(default=0)
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='invaders_game', default=1)
    player = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    score = models.IntegerField(default=0)
    game_over = models.BooleanField(default=False)

#########################################################################################################

