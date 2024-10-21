
# tournaments/models.py
from django.db import models
from django.contrib.auth.models import User
from users.models import Game
import random


class Tournament(models.Model):
    creator = models.ForeignKey(User, related_name='tournaments_created', on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='tournaments_participated')
    winner = models.ForeignKey(User, related_name='tournaments_won', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'Tournament by {self.creator} with {self.participants.count()} participants'

    def initialize_games(self):
        participants = list(self.participants.all())
        random.shuffle(participants)  # Mélange aléatoire des participants

        for i in range(0, len(participants), 2):
            if i + 1 < len(participants):
                Game.objects.create(player1=participants[i], player2=participants[i+1], tournament=self)

