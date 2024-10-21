# pong/management/commands/move_ball.py

from django.core.management.base import BaseCommand
from pongapi2d.models import Game

class Command(BaseCommand):
    help = 'Move the ball in the Pong game'

    def add_arguments(self, parser):
        parser.add_argument('game_id', type=int)

    def handle(self, *args, **options):
        game = Game.objects.get(id=options['game_id'])
        game.ball_position_x += game.ball_velocity_x
        game.ball_position_y += game.ball_velocity_y

        # Vérifier les collisions avec les murs
        if game.ball_position_x <= 0 or game.ball_position_x >= 100:
            game.ball_velocity_x = -game.ball_velocity_x

        if game.ball_position_y <= 0 or game.ball_position_y >= 100:
            game.ball_velocity_y = -game.ball_velocity_y

        game.save()
        self.stdout.write(self.style.SUCCESS(f'Ball moved to ({game.ball_position_x}, {game.ball_position_y})'))
