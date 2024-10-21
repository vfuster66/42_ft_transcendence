
# pong3d/views.py

#########################################################################################################

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from rest_framework import generics
from users.models import Game
from .serializers import GameSerializer
from users.serializers import UserProfileSerializer
from django.conf import settings
import redis
from django.views import View

#########################################################################################################

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

#########################################################################################################

class GameCreateUpdateView(generics.CreateAPIView, generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

def get_online_players(request):
    online_players = r.smembers('online_players')  # Supposons que tu utilises un Set Redis
    players_data = [
        {"username": player.decode("utf-8")} for player in online_players
    ]
    return JsonResponse(players_data, safe=False)

@login_required
def game3D(request):
    print("Accès à la vue du jeu")
    return render(request, 'game/index.html')

@login_required
def get_active_players(request):
    # Cette implémentation dépend de la manière dont tu traces les utilisateurs connectés
    active_users = User.objects.filter(is_online=True)  # Exemple hypothétique
    serializer = UserProfileSerializer(active_users, many=True)
    return JsonResponse(serializer.data, safe=False)

@login_required
def get_player_info(request, player_id):
    try:
        user_profile = UserProfile.objects.get(user__pk=player_id)
        serializer = UserProfileSerializer(user_profile)
        return JsonResponse(serializer.data)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@csrf_exempt
@login_required
def post_game_results(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        player1_id = data.get('player1_id')
        player2_id = data.get('player2_id')
        player1_score = data.get('player1_score')
        player2_score = data.get('player2_score')
        winner_id = data.get('winner_id')
        is_vs_ai = data.get('is_vs_ai', False)

        player1 = User.objects.get(id=player1_id) if player1_id else None
        player2 = User.objects.get(id=player2_id)
        winner = User.objects.get(id=winner_id) if winner_id else None

        won = False
        if winner and player1 and winner == player1:
            won = True
        elif winner and player2 and winner == player2:
            won = True

        game = Game.objects.create(
            player1=player1,
            player2=player2,
            player1_score=player1_score,
            player2_score=player2_score,
            winner=winner,
            completed=True,
            is_vs_ai=is_vs_ai,
            won=won
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

#########################################################################################################