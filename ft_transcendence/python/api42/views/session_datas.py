# views/session_datas.py
from django.http import JsonResponse, HttpResponse
from django.contrib.sessions.models import Session
from ..models import User
from django.middleware.csrf import get_token


def get_session_data(request):
    # Get CSRF token
    get_token(request)
    # Get session key from client-side cookies
    session_key = request.COOKIES.get('sessionid')
    # Retrieve session data from the database
    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        return JsonResponse(session_data)
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=200)




def remove_session_data(request):
    # Get session key from client-side cookies
    session_key = request.COOKIES.get('sessionid')
    # Delete session data from the database
    try:
        session = Session.objects.get(session_key=session_key)
        session.delete()
        return JsonResponse({'message': 'Session deleted successfully'})
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=200)




def fill_session_with_user_info(request, user):
    session = request.session
    session['user'] = user.login
    session['is_authenticated'] = True
    session['img'] = user.image_link
    session['id'] = user.id
    session['email'] = user.email
    session['first_name'] = user.first_name
    session['last_name'] = user.last_name
    session['score'] = user.score
    session['win_games'] = user.win_games
    session['total_games'] = user.total_games
    session['loginWithApi'] = user.loginWithApi
    session['nb_players'] = 1
    session['gamesHistory'] = user.gamesHistory
    session['friends'] = list(user.friends.all().values())



def get_user_from_request(request):
    session_key = request.COOKIES.get('sessionid')
    # Retrieve session data from the database
    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()

        user_login = session_data.get('user')
        if user_login is None:
            return None

        try:
            user = User.objects.filter(login=user_login).first()
            return user
        except User.DoesNotExist:
            return None

    except Session.DoesNotExist:
        return None


def get_highscores(request):
    data = list(User.objects.all().values().order_by('-score')[:10])
    return JsonResponse(data, safe=False)

def update_score(request):
    if request.method == 'POST':
        player_name = request.POST.get('player')
        new_score = int(request.POST.get('score'))
        won = int(request.POST.get('won'))
        opponent = request.POST.get('opponent')
        playerPoints = request.POST.get('playerPoints')
        opponentPoints = request.POST.get('opponentPoints')

        try:
            player = User.objects.get(login=player_name)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Joueur introuvable'}, status=404)

        player_old_score = player.score
        if player.gamesHistory:
            player.gamesHistory += f"{opponent} : {playerPoints} / {opponentPoints}\n"
        else:
            player.gamesHistory = f"{opponent} : {playerPoints} / {opponentPoints}\n"

        if (won):
            player.score += new_score
            player.win_games += 1
        else :
            player.score += new_score
        player.total_games += 1
        player.save()

        return JsonResponse({
            'status': 'success',
            'player': player_name,
            'old_score': player_old_score,
            'new_score': player.score
        }, status=200)
    else:
        return JsonResponse({'status': 'bad request'}, status=400)
