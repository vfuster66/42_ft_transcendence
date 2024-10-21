# pong/management/commands/start_game.py

from django.core.management.base import BaseCommand
from pongapi2d.models import Game
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Start a new Pong game'

    def add_arguments(self, parser):
        parser.add_argument('player1_id', type=int)
        parser.add_argument('player2_id', type=int)

    def handle(self, *args, **options):
        player1 = User.objects.get(id=options['player1_id'])
        player2 = User.objects.get(id=options['player2_id'])
        game = Game.objects.create(player1=player1, player2=player2)
        self.stdout.write(self.style.SUCCESS(f'Game {game.id} started between {player1.username} and {player2.username}'))
