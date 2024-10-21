
# tournaments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Tournament
from users.models import Game
from users.models import UserProfile
from django.contrib.auth.models import User
from users.serializers import UserProfileSerializer
from django.http import JsonResponse
import json
import logging
import random
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


logger = logging.getLogger(__name__)


@login_required
def tournament_pong2d_pvp(request, player1_id, player2_id, tournament_id, match_id):
    player1 = get_object_or_404(UserProfile, user_id=player1_id)
    player2 = get_object_or_404(UserProfile, user_id=player2_id)

    player1_serializer = UserProfileSerializer(player1, context={'request': request})
    player2_serializer = UserProfileSerializer(player2, context={'request': request})

    context = {
        'player1': player1_serializer.data,
        'player2': player2_serializer.data,
        'is_tournament_mode': True,
        'tournament_id': tournament_id,
        'match_id': match_id,
        'player1_id': player1_id,
        'player2_id': player2_id,
    }
    return render(request, 'tournaments/tournament_pong2d_pvp.html', context)

def notify_user_about_tournament(user, tournament):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            'type': 'send_tournament_notification',
            'tournament_id': tournament.id,
            'message': f"Vous êtes attendu pour participer au tournoi {tournament.id}."
        }
    )

@login_required
def create_tournament(request):
    if request.method == 'POST':
        participants_ids = request.POST.getlist('participants')
        participants = User.objects.filter(id__in=participants_ids)

        if len(participants) != 7:
            return redirect('create_tournament')

        tournament = Tournament.objects.create(creator=request.user)
        tournament.participants.set(participants)
        tournament.participants.add(request.user)
        tournament.save()

        tournament.initialize_games()

        # Envoyer des notifications
        for participant in participants:
            if participant != request.user:
                notify_user_about_tournament(participant, tournament)
                logger.info(f"Tournament notification sent to user {participant.id} for tournament {tournament.id}")

        return redirect('tournament_details', tournament_id=tournament.id)

    online_users = UserProfile.objects.filter(status='ONLINE').exclude(user=request.user)
    context = {
        'online_users': online_users
    }
    return render(request, 'tournaments/create_tournament.html', context)

@login_required
def matchmaking(request):
    try:
        online_users = list(User.objects.filter(profile__status='ONLINE').exclude(id=request.user.id))
        if len(online_users) < 7:
            return JsonResponse({'status': 'error', 'message': 'Not enough online users for matchmaking.'}, status=400)

        selected_users = random.sample(online_users, 7)
        selected_users.append(request.user)

        tournament = Tournament.objects.create(creator=request.user)
        tournament.participants.set(selected_users)
        tournament.save()

        tournament.initialize_games()

        # Envoyer des notifications
        for user in selected_users:
            if user != request.user:
                notify_user_about_tournament(user, tournament)
                logger.info(f"Tournament notification sent to user {user.id} for tournament {tournament.id}")

        return JsonResponse({'status': 'success', 'redirect_url': f"/tournament_details/{tournament.id}/"})
    except Exception as e:
        logger.error(f"Exception occurred during matchmaking: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def tournament_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    games = tournament.games.all()

    context = {
        'tournament': tournament,
        'games': games
    }
    return render(request, 'tournaments/tournament_details.html', context)



@login_required
def tournament_update_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        player1_score = request.POST.get('player1_score')
        player2_score = request.POST.get('player2_score')

        game.player1_score = player1_score
        game.player2_score = player2_score
        game.completed = True

        if int(player1_score) > int(player2_score):
            game.winner = game.player1
        else:
            game.winner = game.player2

        game.save()

        tournament = game.tournament
        if not tournament.games.filter(completed=False).exists():
            advance_to_next_round(tournament)

        return redirect('tournament_details', tournament_id=tournament.id)

    context = {
        'game': game
    }
    return render(request, 'tournaments/update_game.html', context)


def advance_to_next_round(tournament):
    completed_games = tournament.games.filter(completed=True)
    if tournament.games.count() == 4 and completed_games.count() == 4:  # First round completed
        winners = [game.winner for game in completed_games]
        for i in range(0, 4, 2):
            Game.objects.create(player1=winners[i], player2=winners[i+1], tournament=tournament)
    elif tournament.games.count() == 6 and completed_games.count() == 6:  # Semi-finals completed
        # Get the winners from the semi-final games only (games 5 and 6)
        semifinal_games = completed_games.filter(id__in=[game.id for game in tournament.games.all()][4:6])
        winners = [game.winner for game in semifinal_games]
        Game.objects.create(player1=winners[0], player2=winners[1], tournament=tournament)
    elif tournament.games.count() == 7 and completed_games.count() == 7:  # Final completed
        final_game = completed_games.last()
        tournament.winner = final_game.winner
        tournament.completed = True
        tournament.save()


@csrf_exempt
def pong2d_tournament_match_end(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.debug(f"Received pong2d_tournament_match_end POST request: {data}")
            match_id = data.get('match_id')
            winner_id = data.get('winner')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')

            logger.debug(f"pong2d_tournament_match_end -> Match ID: {match_id}")
            logger.debug(f"pong2d_tournament_match_end -> Winner ID: {winner_id}")
            logger.debug(f"pong2d_tournament_match_end -> Player 1 ID: {player1_score}")
            logger.debug(f"pong2d_tournament_match_end -> Player 2 ID: {player2_score}")

            game = Game.objects.get(id=match_id)
            winner = User.objects.get(id=winner_id)

            game.winner = winner
            game.player1_score = player1_score
            game.player2_score = player2_score
            game.completed = True
            game.save()

            tournament = game.tournament
            advance_to_next_round(tournament)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid method'}, status=405)


#########################################################################################

@login_required
def tournament_pongapi2d_pvp(request, player1_id, player2_id, tournament_id, match_id):
    player1 = get_object_or_404(UserProfile, user_id=player1_id)
    player2 = get_object_or_404(UserProfile, user_id=player2_id)

    player1_serializer = UserProfileSerializer(player1, context={'request': request})
    player2_serializer = UserProfileSerializer(player2, context={'request': request})

    context = {
        'player1': player1_serializer.data,
        'player2': player2_serializer.data,
        'is_tournament_mode': True,
        'tournament_id': tournament_id,
        'match_id': match_id,
        'player1_id': player1_id,
        'player2_id': player2_id,
    }
    return render(request, 'tournaments/tournament_pongapi2d_pvp.html', context)


@login_required
def create_api_tournament(request):
    if request.method == 'POST':
        participants_ids = request.POST.getlist('participants')
        participants = User.objects.filter(id__in=participants_ids)

        if len(participants) != 7:
            return redirect('create_api_tournament')

        tournament = Tournament.objects.create(creator=request.user)
        tournament.participants.set(participants)
        tournament.participants.add(request.user)
        tournament.save()

        tournament.initialize_games()

        return redirect('tournament_api_details', tournament_id=tournament.id)

    online_users = UserProfile.objects.filter(status='ONLINE').exclude(user=request.user)
    context = {
        'online_users': online_users
    }
    return render(request, 'tournaments/create_api_tournament.html', context)

@login_required
def matchmaking_api(request):
    try:
        online_users = list(User.objects.filter(profile__status='ONLINE').exclude(id=request.user.id))
        if len(online_users) < 7:
            return JsonResponse({'status': 'error', 'message': 'Not enough online users for matchmaking.'}, status=400)

        selected_users = random.sample(online_users, 7)
        selected_users.append(request.user)

        tournament = Tournament.objects.create(creator=request.user)
        tournament.participants.set(selected_users)
        tournament.save()

        tournament.initialize_games()

        return JsonResponse({'status': 'success', 'redirect_url': f"/tournament_api_details/{tournament.id}/"})
    except Exception as e:
        logger.error(f"Exception occurred during matchmaking: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def tournament_api_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    games = tournament.games.all()

    context = {
        'tournament': tournament,
        'games': games
    }
    return render(request, 'tournaments/tournament_api_details.html', context)


@login_required
def tournament_api_update_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        player1_score = request.POST.get('player1_score')
        player2_score = request.POST.get('player2_score')

        game.player1_score = player1_score
        game.player2_score = player2_score
        game.completed = True

        if int(player1_score) > int(player2_score):
            game.winner = game.player1
        else:
            game.winner = game.player2

        game.save()

        tournament = game.tournament
        if not tournament.games.filter(completed=False).exists():
            api_advance_to_next_round(tournament)

        return redirect('tournament_api_details', tournament_id=tournament.id)

    context = {
        'game': game
    }
    return render(request, 'tournaments/tournament_api_update_game.html', context)


def api_advance_to_next_round(tournament):
    completed_games = tournament.games.filter(completed=True)
    if tournament.games.count() == 4 and completed_games.count() == 4:  # First round completed
        winners = [game.winner for game in completed_games]
        for i in range(0, 4, 2):
            Game.objects.create(player1=winners[i], player2=winners[i+1], tournament=tournament)
    elif tournament.games.count() == 6 and completed_games.count() == 6:  # Semi-finals completed
        # Get the winners from the semi-final games only (games 5 and 6)
        semifinal_games = completed_games.filter(id__in=[game.id for game in tournament.games.all()][4:6])
        winners = [game.winner for game in semifinal_games]
        Game.objects.create(player1=winners[0], player2=winners[1], tournament=tournament)
    elif tournament.games.count() == 7 and completed_games.count() == 7:  # Final completed
        final_game = completed_games.last()
        tournament.winner = final_game.winner
        tournament.completed = True
        tournament.save()


@csrf_exempt
def pongapi2d_tournament_match_end(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.debug(f"Received pongapi2d_tournament_match_end POST request: {data}")
            match_id = data.get('match_id')
            winner_id = data.get('winner')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')

            logger.debug(f"pongapi2d_tournament_match_end -> Match ID: {match_id}")
            logger.debug(f"pongapi2d_tournament_match_end -> Winner ID: {winner_id}")
            logger.debug(f"pongapi2d_tournament_match_end -> Player 1 ID: {player1_score}")
            logger.debug(f"pongapi2d_tournament_match_end -> Player 2 ID: {player2_score}")

            game = Game.objects.get(id=match_id)
            winner = User.objects.get(id=winner_id)

            game.winner = winner
            game.player1_score = player1_score
            game.player2_score = player2_score
            game.completed = True
            game.save()

            tournament = game.tournament
            api_advance_to_next_round(tournament)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid method'}, status=405)


