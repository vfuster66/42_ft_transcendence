#########################################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from users.models import UserProfile, Game
from django.contrib.auth.models import User
from users.serializers import UserProfileSerializer
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone

# Configure logger
logger = logging.getLogger(__name__)

#########################################################################################################

def pong2d_mode(request):
    logger.info("Accès à la page pong2d_mode par l'utilisateur %s", request.user)
    return render(request, 'pong2d/pong2d_mode.html')

def pong2d_choose(request):
    player1_id = request.user.id
    logger.info("Utilisateur %s choisit un joueur pour le match", player1_id)

    if request.method == 'POST':
        player2_id = request.POST.get('player2_id')
        logger.info("Formulaire POST soumis par l'utilisateur %s avec player2_id: %s", player1_id, player2_id)

        if not player2_id:
            logger.warning("player2_id manquant dans la soumission du formulaire par l'utilisateur %s", player1_id)
            return redirect('pong2d_choose') 

        game = Game.objects.create(player1_id=player1_id, player2_id=player2_id)
        logger.info("Nouveau jeu créé entre player1_id: %s et player2_id: %s", player1_id, player2_id)

        return redirect(reverse('pong2d_pvp', args=[player1_id, player2_id]))

    online_users = UserProfile.objects.filter(status='ONLINE').exclude(user=request.user)
    logger.info("Utilisateurs en ligne récupérés pour l'utilisateur %s: %s", player1_id, list(online_users))
    context = {
        'online_users': online_users
    }
    return render(request, 'pong2d/pong2d_choose.html', context)

#########################################################################################################

# player_vs_player

@login_required
def pong2d_pvp(request, player1_id, player2_id):
    logger.info("Accès à la page pong2d_pvp par l'utilisateur %s", request.user)
    
    player1_profile = get_object_or_404(UserProfile, user_id=player1_id)
    player2_profile = get_object_or_404(UserProfile, user_id=player2_id)

    player1_serializer = UserProfileSerializer(player1_profile, context={'request': request})
    player2_serializer = UserProfileSerializer(player2_profile, context={'request': request})

    new_game = Game.objects.create(
        player1_id=player1_id,
        player2_id=player2_id,
        game_type='pong2d',
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

    logger.info("Contexte pour pong2d_pvp: %s", context)
    return render(request, 'pong2d/pong2d_pvp.html', context)



def pong2d_pvp_success(request):
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
    logger.info("Contexte pour pong2d_pvp_success: %s", context)
    return render(request, 'pong2d/pong2d_pvp_success.html', context)

@csrf_exempt
def pong2d_match_end(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.debug(f"Received pong2d_match_end POST request: {data}")
            match_id = data.get('match_id')
            winner_id = data.get('winner')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')

            logger.debug(f"pong2d_match_end -> Match ID: {match_id}")
            logger.debug(f"pong2d_match_end -> Winner ID: {winner_id}")
            logger.debug(f"pong2d_match_end -> Player 1 Score: {player1_score}")
            logger.debug(f"pong2d_match_end -> Player 2 Score: {player2_score}")

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
                response['redirect_url'] = reverse('tournament_details', args=[data['tournament_id']])
            else:
                response['redirect_url'] = (reverse('pong2d_pvp_success') + 
                                            f"?player1Score={player1_score}&player2Score={player2_score}")

            return JsonResponse(response)
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    logger.warning("Invalid method for pong2d_match_end: %s", request.method)
    return JsonResponse({'status': 'invalid method'}, status=405)

#########################################################################################################

# player_vs_ia


@login_required
def pong2d_ia(request):
    logger.info("Accès à la page pong2d_ia par l'utilisateur %s", request.user)
    
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_serializer = UserProfileSerializer(user_profile, context={'request': request})
    
    ai_user = get_object_or_404(User, username='AI')
    # Créer un nouvel objet Game pour générer match_id
    new_game = Game.objects.create(
        player1=request.user,
        player2=ai_user,
        game_type='pong2d',
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
    
    logger.info("Contexte pour pong2d_ia: %s", context)
    return render(request, 'pong2d/pong2d_ia.html', context)


def pong2d_success(request):
    player1_score = int(request.GET.get('player1Score', 0))
    ai_score = int(request.GET.get('aiScore', 0))
    
    logger.info("Succès du jeu contre l'IA avec scores - Player1: %d, AI: %d", player1_score, ai_score)
    
    context = {
        'player1_score': player1_score,
        'ai_score': ai_score
    }
    
    logger.info("Contexte pour pong2d_success: %s", context)
    return render(request, 'pong2d/pong2d_success.html', context)


def pong2d_failure(request):
    player1_score = int(request.GET.get('player1Score', 0))
    ai_score = int(request.GET.get('aiScore', 0))
    
    logger.info("Échec du jeu contre l'IA avec scores - Player1: %d, AI: %d", player1_score, ai_score)
    
    context = {
        'player1_score': player1_score,
        'ai_score': ai_score
    }
    
    logger.info("Contexte pour pong2d_failure: %s", context)
    return render(request, 'pong2d/pong2d_failure.html', context)


@csrf_exempt
def pong2d_ia_end_match(request):
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
            game_type='pong2d',
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

