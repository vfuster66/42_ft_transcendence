
# pongapi2d/views.py

#########################################################################################################

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets
from pongapi2d.models import Pongapi2dGame, Pongapi2dAIGame
from users.models import Game, UserProfile, User
from users.serializers import UserProfileSerializer
from .serializers import Pongapi2dGameSerializer, Pongapi2dAIGameSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

#########################################################################################################

# Configure logging

logger = logging.getLogger('django')

#########################################################################################################

class GameViewSet(viewsets.ModelViewSet):
    queryset = Pongapi2dGame.objects.all()
    serializer_class = Pongapi2dGameSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def move_ball(self, request, pk=None):
        game = self.get_object()
        logger.debug(f'Moving ball for game {game.id}')
        try:
            game.update_ball_position()
            logger.info(f'Ball position updated to ({game.ball_position_x}, {game.ball_position_y}) for game {game.id}')
        except Exception as e:
            logger.error(f'Error moving ball for game {game.id}: {e}')
            return Response({'error': 'An error occurred while moving the ball'}, status=500)
        return Response(Pongapi2dGameSerializer(game).data)

    @action(detail=True, methods=['post'])
    def move_paddle(self, request, pk=None):
        game = self.get_object()
        player = request.user
        position = request.data.get('position')
        logger.debug(f'Player {player.username} is moving paddle in game {game.id} to position {position}')

        try:
            if player == game.player1:
                game.player1_paddle_position = position
            elif player == game.player2:
                game.player2_paddle_position = position
            game.save()
            logger.info(f'Paddle position updated to {position} for player {player.username} in game {game.id}')
        except Exception as e:
            logger.error(f'Error moving paddle for game {game.id}: {e}')
            return Response({'error': 'An error occurred while moving the paddle'}, status=500)

        return Response(Pongapi2dGameSerializer(game).data)
    
#########################################################################################################

class AIGameViewSet(viewsets.ModelViewSet):
    queryset = Pongapi2dAIGame.objects.all()
    serializer_class = Pongapi2dAIGameSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def move_ball(self, request, pk=None):
        game = self.get_object()
        logger.debug(f'Moving ball for AI game {game.id}')
        try:
            game.update_ball_position()
            logger.info(f'Ball position updated to ({game.ball_position_x}, {game.ball_position_y}) for AI game {game.id}')
        except Exception as e:
            logger.error(f'Error moving ball for AI game {game.id}: {e}')
            return Response({'error': 'An error occurred while moving the ball'}, status=500)
        return Response(Pongapi2dAIGameSerializer(game).data)

    @action(detail=True, methods=['post'])
    def move_paddle(self, request, pk=None):
        game = self.get_object()
        player = request.user
        position = request.data.get('position')
        logger.debug(f'Player {player.username} is moving paddle in AI game {game.id} to position {position}')

        try:
            if player == game.player1:
                game.player1_paddle_position = position
            elif player == game.player2:
                game.player2_paddle_position = position
            game.save()
            logger.info(f'Paddle position updated to {position} for player {player.username} in AI game {game.id}')
        except Exception as e:
            logger.error(f'Error moving paddle for AI game {game.id}: {e}')
            return Response({'error': 'An error occurred while moving the paddle'}, status=500)

        return Response(Pongapi2dAIGameSerializer(game).data)

    @action(detail=True, methods=['post'])
    def move_ai_paddle(self, request, pk=None):
        game = self.get_object()
        logger.debug(f'Moving AI paddle for game {game.id}')
        try:
            if game.ai_difficulty == 'easy':
                delay = 5
            elif game.ai_difficulty == 'medium':
                delay = 3
            else:
                delay = 1

            if game.ball_position_x > game.ball_position_x + delay:
                game.player2_paddle_position += 1
            elif game.ball_position_x < game.ball_position_x - delay:
                game.player2_paddle_position -= 1

            game.save()
            logger.info(f'AI paddle moved for game {game.id}')
        except Exception as e:
            logger.error(f'Error moving AI paddle for game {game.id}: {e}')
            return Response({'error': 'An error occurred while moving the AI paddle'}, status=500)

        return Response(Pongapi2dAIGameSerializer(game).data)
    
#########################################################################################################

# Lancement jeu

def pongapi2d_mode(request):
    logger.info("Accès à la page pong2d_mode par l'utilisateur %s", request.user)
    return render(request, 'pongapi2d/pongapi2d_mode.html')

def pongapi2d_choose(request):
    player1_id = request.user.id
    logger.info("Utilisateur %s choisit un joueur pour le match", player1_id)

    if request.method == 'POST':
        player2_id = request.POST.get('player2_id')
        logger.info("Formulaire POST soumis par l'utilisateur %s avec player2_id: %s", player1_id, player2_id)

        if not player2_id:
            logger.warning("player2_id manquant dans la soumission du formulaire par l'utilisateur %s", player1_id)
            return redirect('pongapi2d_choose') 

        game = Game.objects.create(player1_id=player1_id, player2_id=player2_id)
        logger.info("Nouveau jeu créé entre player1_id: %s et player2_id: %s", player1_id, player2_id)

        return redirect(reverse('pongapi2d_pvp', args=[player1_id, player2_id]))

    online_users = UserProfile.objects.filter(status='ONLINE').exclude(user=request.user)
    logger.info("Utilisateurs en ligne récupérés pour l'utilisateur %s: %s", player1_id, list(online_users))
    context = {
        'online_users': online_users
    }
    return render(request, 'pongapi2d/pongapi2d_choose.html', context)

#########################################################################################################

# player_vs_player

@login_required
def pongapi2d_pvp(request, player1_id, player2_id):
    logger.info("Accès à la page pong2d_pvp par l'utilisateur %s", request.user)
    
    player1_profile = get_object_or_404(UserProfile, user_id=player1_id)
    player2_profile = get_object_or_404(UserProfile, user_id=player2_id)

    player1_serializer = UserProfileSerializer(player1_profile, context={'request': request})
    player2_serializer = UserProfileSerializer(player2_profile, context={'request': request})

    new_game = Game.objects.create(
        player1_id=player1_id,
        player2_id=player2_id,
        game_type='pongapi2d',
        winner=None,
        player1_score=0,
        player2_score=0,
        completed=False,
        game_date=timezone.now(),
        is_vs_ai=False
    )
    match_id = new_game.id
    
    context = {
        'player1': player1_serializer.data,
        'player2': player2_serializer.data,
        'is_tournament_mode': False,
        'match_id': match_id,
        'player1_id': player1_id,
        'player2_id': player2_id,
    }

    logger.info("Contexte pour pongapi2d_pvp: %s", context)
    return render(request, 'pongapi2d/pongapi2d_pvp.html', context)



def pongapi2d_pvp_success(request):
    player1 = 'Player 1'
    player2 = 'Player 2'
    player1_score = int(request.GET.get('player1Score', 0))
    player2_score = int(request.GET.get('player2Score', 0))
    
    winner = player1 if player1_score > player2_score else player2
    
    context = {
        'winner': winner,
        'player1': player1,
        'player2': player2,
        'player1_score': player1_score,
        'player2_score': player2_score
    }
    logger.info("Contexte pour pongapi2d_pvp_success: %s", context)
    return render(request, 'pongapi2d/pongapi2d_pvp_success.html', context)

@csrf_exempt
def pongapi2d_match_end(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.debug(f"Received pongapi2d_match_end POST request: {data}")
            match_id = data.get('match_id')
            winner_id = data.get('winner')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')

            game = Game.objects.get(id=match_id)
            winner = User.objects.get(id=winner_id)

            game.winner = winner
            game.player1_score = player1_score
            game.player2_score = player2_score
            game.completed = True
            game.save()

            response = {'status': 'success'}
            logger.info(f"Match {match_id} terminé. Gagnant: {winner_id}, Scores - Player1: {player1_score}, Player2: {player2_score}")

            if 'is_tournament_mode' in data and data['is_tournament_mode']:
                response['redirect_url'] = reverse('tournament_api_details', args=[data['tournament_id']])
            else:
                response['redirect_url'] = (reverse('pongapi2d_pvp_success') + 
                                            f"?player1Score={player1_score}&player2Score={player2_score}")

            return JsonResponse(response)
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    logger.warning("Invalid method for pongapi2d_match_end: %s", request.method)
    return JsonResponse({'status': 'invalid method'}, status=405)
#########################################################################################################


@login_required
def pongapi2d_ia(request):
    logger.info("Accès à la page pongapi2d_ia par l'utilisateur %s", request.user)
    
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_serializer = UserProfileSerializer(user_profile, context={'request': request})
    
    ai_user = get_object_or_404(User, username='AI')
    new_game = Game.objects.create(
        player1=request.user,
        player2=ai_user,
        game_type='pongapi2d',
        winner=None,
        player1_score=0,
        player2_score=0,
        completed=False,
        game_date=timezone.now(),
        is_vs_ai=True
    )
    match_id = new_game.id
    player_id = request.user.id
    
    context = {
        'user': user_serializer.data,
        'match_id': match_id,
        'player_id': player_id,
    }
    
    logger.info("Contexte pour pongapi2d_ia: %s", context)
    return render(request, 'pongapi2d/pongapi2d_ia.html', context)


def pongapi2d_success(request):
    player1_score = int(request.GET.get('player1Score', 0))
    ai_score = int(request.GET.get('aiScore', 0))
    
    logger.info("Succès du jeu contre l'IA avec scores - Player1: %d, AI: %d", player1_score, ai_score)
    
    context = {
        'player1_score': player1_score,
        'ai_score': ai_score
    }
    
    logger.info("Contexte pour pongapi2d_success: %s", context)
    return render(request, 'pongapi2d/pongapi2d_success.html', context)


def pongapi2d_failure(request):
    player1_score = int(request.GET.get('player1Score', 0))
    ai_score = int(request.GET.get('aiScore', 0))
    
    logger.info("Échec du jeu contre l'IA avec scores - Player1: %d, AI: %d", player1_score, ai_score)
    
    context = {
        'player1_score': player1_score,
        'ai_score': ai_score
    }
    
    logger.info("Contexte pour pongapi2d_failure: %s", context)
    return render(request, 'pongapi2d/pongapi2d_failure.html', context)


@csrf_exempt
def pongapi2d_ia_end_match(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        player1_score = data.get('player1_score')
        ai_score = data.get('ai_score')
        winner_name = data.get('winner')
        user = request.user

        if winner_name == 'Player 1':
            winner = user
        else:
            winner = None

        game = Game.objects.create(
            player1=user,
            player2=None,
            game_type='pongapi2d',
            winner=winner,
            player1_score=player1_score,
            player2_score=ai_score,
            completed=True,
            game_date=timezone.now(),
            is_vs_ai=True
        )

        response_data = {
            'message': 'Match results recorded successfully',
            'player1_score': player1_score,
            'ai_score': ai_score,
            'winner': winner_name
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

