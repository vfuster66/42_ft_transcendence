
# pongapi2d/models.py

#########################################################################################################

from django.db import models
from django.contrib.auth.models import User

from users.models import Game

#########################################################################################################

class Pongapi2dGame(Game):
    ball_position_x = models.FloatField(default=0.0)
    ball_position_y = models.FloatField(default=0.0)
    ball_velocity_x = models.FloatField(default=1.0)
    ball_velocity_y = models.FloatField(default=1.0)
    player1_paddle_position = models.FloatField(default=0.0)
    player2_paddle_position = models.FloatField(default=0.0)
    game_over = models.BooleanField(default=False)

    def update_ball_position(self):
        self.ball_position_x += self.ball_velocity_x
        self.ball_position_y += self.ball_velocity_y

        if self.ball_position_x <= 0 or self.ball_position_x >= 100:
            self.ball_velocity_x = -self.ball_velocity_x

        if self.ball_position_y <= 0 or self.ball_position_y >= 100:
            self.ball_velocity_y = -self.ball_velocity_y

        self.save()

#########################################################################################################

class Pongapi2dAIGame(Pongapi2dGame):
    ai_difficulty = models.CharField(max_length=50, default='medium')

#########################################################################################################

