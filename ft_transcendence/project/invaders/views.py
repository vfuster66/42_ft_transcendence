from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Player
from users.models import Game
from tournaments.models import Tournament
from users.models import UserProfile
from users.serializers import UserProfileSerializer
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import random
import logging
from django.urls import reverse
from django.utils import timezone

##############################################################################################

logger = logging.getLogger(__name__)

##############################################################################################

# Lancement jeu

@login_required
def select_mode(request):
    return render(request, 'invaders/select_mode.html')

##############################################################################################

# Mode Solo

def invaders_solo(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile_serializer = UserProfileSerializer(user_profile, context={'request': request})

    dummy_user = get_object_or_404(User, username='dummy_user')

    game = Game.objects.create(
        player1=request.user,
        player2=dummy_user,
        game_type='invaders',
        winner=None,
        player1_score=0,
        player2_score=0,
        completed=False,
        game_date=timezone.now(),
        is_vs_ai=False,
        tournament_id=None
    )

    match_id = game.id

    Player.objects.create(
        player=request.user,
        game=game,
        username=request.user.username
    )

    context = {
        'user_profile': user_profile_serializer.data,
        'match_id': match_id,
    }

    logger.debug(f"context: {context}")

    return render(request, 'invaders/invaders_solo.html', context)

##############################################################################################

# Fin de partie

def invaders_tournament(request):
    #match_id = request.GET.get('match_id', None)
    #is_tournament_mode = match_id is not None
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile_serializer = UserProfileSerializer(user_profile, context={'request': request})

    is_tournament_mode = request.GET.get('is_tournament_mode', 'false')
    tournament_id = request.GET.get('tournament_id', None)
    match_id = request.GET.get('match_id', None)

    context = {
        'user_profile': user_profile_serializer.data,
        'is_tournament_mode': is_tournament_mode,
        'tournament_id': tournament_id,
        'match_id': match_id,
    }
    return render(request, 'invaders/invaders_tournament.html', context)


def invaders_win(request):
    score = request.GET.get('score', 0)
    lives = request.GET.get('lives', 0)
    context = {
        'score': score,
        'lives': lives
    }
    return render(request, 'invaders/invaders_win.html', context)


def invaders_lose(request):
    score = request.GET.get('score', 0)
    lives = request.GET.get('lives', 0)
    context = {
        'score': score,
        'lives': lives
    }
    return render(request, 'invaders/invaders_lose.html', context)

#########################################################################################################

# tournois


@login_required
def create_invaders_tournament(request):
    if request.method == 'POST':
        if 'matchmaking' in request.POST:
            participants = list(UserProfile.objects.filter(status='ONLINE').exclude(user=request.user))
            selected_participants = random.sample(participants, 3) + [request.user.profile]
        else:
            participants_ids = request.POST.getlist('participants')
            selected_participants = list(UserProfile.objects.filter(id__in=participants_ids)) + [request.user.profile]

        if len(selected_participants) != 4:
            return redirect('create_invaders_tournament')

        tournament = Tournament.objects.create(creator=request.user)
        tournament.participants.set([p.user for p in selected_participants])
        tournament.save()

        # Utiliser un utilisateur fictif pour player2
        dummy_user = User.objects.get_or_create(username='dummy_user')[0]

        # Créer les jeux et les joueurs pour chaque participant
        for participant in selected_participants:
            game = Game.objects.create(player1=participant.user, player2=dummy_user, game_type='invaders', tournament=tournament)
            Player.objects.create(player=participant.user, game=game)

        return redirect('invaders_tournament_details', tournament_id=tournament.id)

    online_users = UserProfile.objects.filter(status='ONLINE').exclude(user=request.user)
    return render(request, 'invaders/create_invaders_tournament.html', {'online_users': online_users})


@login_required
def invaders_tournament_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    games = tournament.games.all()

    context = {
        'tournament': tournament,
        'games': games
    }
    return render(request, 'invaders/invaders_tournament_details.html', context)


@csrf_exempt
def invaders_match_end(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            match_id = data.get('match_id')
            score = data.get('score')

            game = Game.objects.get(id=match_id)
            player = Player.objects.get(game=game)
            player.score = score
            player.game_over = True
            player.save()

            tournament = game.tournament
            if not tournament.games.filter(invaders_game__game_over=False).exists():
                # Calculate the winner based on high scores
                top_player = Player.objects.filter(game__tournament=tournament).order_by('-score').first()
                if top_player:
                    tournament.winner = top_player.player
                    tournament.completed = True
                    tournament.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid method'}, status=405)

##############################################################################################

