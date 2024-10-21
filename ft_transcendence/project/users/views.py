
# users/views.py

#########################################################################################################

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.db.models import Max, Avg, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext as _
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from io import BytesIO
from PIL import Image
from requests_oauthlib import OAuth2Session
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from two_factor.utils import devices_for_user

from .forms import SignUpForm, UserProfileForm, UserProfile, CustomAuthenticationForm
from .models import Game, UserProfile
from .serializers import UserProfileSerializer, GameSerializer
from tournaments.models import Tournament
from invaders.models import Player as InvadersPlayer, Game as InvadersGame

import base64
import logging
import os
import qrcode
import qrcode.image.svg
import requests
import urllib
import uuid

#########################################################################################################

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=True, methods=['get'])
    def games(self, request, pk=None):
        user = self.get_object().user
        games_as_player1 = Game.objects.filter(player1=user)
        games_as_player2 = Game.objects.filter(player2=user)
        games = games_as_player1.union(games_as_player2).order_by('-game_date')
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

#########################################################################################################

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

#########################################################################################################

logger = logging.getLogger(__name__)

#########################################################################################################

# Inscription

def signup(request):
    logger.info("Signup view accessed")
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('consent'):
                user = form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                logger.info(f"User created and logged in: {user.username}")
                return redirect('home')
            else:
                form.add_error('consent', 'Vous devez accepter les termes pour continuer.')
        else:
            logger.warning("Signup form is not valid")
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

#########################################################################################################

# Base view

def base(request):
    logger.info("Base view accessed")
    langue_actuelle = get_language()  # Récupération de la langue courante
    return render(request, 'base.html', {'langue': langue_actuelle})

#########################################################################################################

# Connexion

def connexion(request):
    logger.info("Connexion view accessed")
    return render(request, 'users/connexion.html')

#########################################################################################################

# Login

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    extra_context = {'page_title': 'Login'}

    @method_decorator(csrf_protect)
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            logger.info(f"User {username} authenticated successfully.")
            user_profile = UserProfile.objects.filter(user=user).first()
            if user_profile and user_profile.two_factor_enabled:
                logger.info(f"2FA is enabled for user {username}.")
                token = form.cleaned_data.get('token')
                if token:
                    if any(device.verify_token(token) for device in devices_for_user(user, confirmed=True)):
                        logger.info(f"2FA token verified for user {username}.")
                        login(self.request, user)
                        return HttpResponseRedirect(self.get_success_url())
                    else:
                        logger.warning(f"Invalid 2FA token for user {username}.")
                        messages.error(self.request, _("Invalid 2FA token."))
                        return self.form_invalid(form)
                else:
                    logger.info(f"2FA token required for user {username}.")
                    self.request.session['show_token'] = True
                    messages.error(self.request, _("This account requires a 2FA token to log in."))
                    return self.form_invalid(form)
            else:
                logger.info(f"2FA is not enabled for user {username}. Logging in without 2FA.")
                login(self.request, user)
                tab_id = self.request.COOKIES.get('tab_id')
                if not tab_id:
                    tab_id = str(uuid.uuid4())
                    logger.debug(f"No tab_id found in cookies. Generated new tab_id={tab_id}.")

                self.request.session[f'user_id_{tab_id}'] = user.id
                logger.debug(f"Associated tab_id={tab_id} with user_id={user.id}")
                
                response = HttpResponseRedirect(reverse_lazy('home'))
                response.set_cookie('tab_id', tab_id)
                logger.debug(f"Set tab_id={tab_id} for user {username}")
                return response
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(self.request, _("Invalid username or password."))
            return self.form_invalid(form)

#########################################################################################################

# Accueil

def home(request):
    logger.info("Home view accessed")
    if not request.user.is_authenticated or not request.user.profile.is_active:
        logger.warning("Unauthorized access attempt to home")
        return redirect('connexion')
    return render(request, 'users/home.html')

#########################################################################################################

# Deconnexion

def logout_message(request):
    logger.info("Logout message view accessed")
    return render(request, 'users/logout.html')


def logout_view(request):
    logger.info("Logout view accessed")
    if request.user.is_authenticated:
        logout(request)
        logger.info(f"User logged out: {request.user.username}")
        return redirect('logout_message')
    else:
        logger.warning("Unauthorized logout attempt")
        return redirect('connexion')

#########################################################################################################

# Connexion 42

def start_oauth(request):
    logger.info("start_oauth view accessed")
    client_id = settings.SOCIAL_AUTH_42_KEY
    redirect_uri = settings.SOCIAL_AUTH_42_REDIRECT_URI
    authorize_url = settings.OAUTH_AUTHORIZE_URL

    scope = ["public", "profile"]

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    authorization_url, state = oauth.authorization_url(authorize_url)
    request.session['oauth_state'] = state
    logger.info(f"Authorization URL generated: {authorization_url}")
    return redirect(authorization_url)


def get_token_from_code(code, state):
    logger.info("get_token_from_code view accessed")
    client_id = settings.SOCIAL_AUTH_42_KEY
    client_secret = settings.SOCIAL_AUTH_42_SECRET
    next_client_secret = settings.NEXT_SOCIAL_AUTH_42_SECRET
    token_url = settings.OAUTH_TOKEN_URL

    redirect_uri = settings.SOCIAL_AUTH_42_REDIRECT_URI
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, state=state)

    try:
        token = oauth.fetch_token(
            token_url,
            client_secret=client_secret,
            code=code,
            include_client_id=True
        )
        logger.info(f"get_token_from_code -> Access token retrieved with primary secret: {token.get('access_token')}")
        return token.get('access_token')
    except Exception as e:
        logger.error(f"Failed to fetch token with primary secret: {e}")

    try:
        token = oauth.fetch_token(
            token_url,
            client_secret=next_client_secret,
            code=code,
            include_client_id=True
        )
        logger.info(f"get_token_from_code -> Access token retrieved with next secret: {token.get('access_token')}")
        return token.get('access_token')
    except Exception as e:
        logger.error(f"Failed to fetch token with next secret: {e}")
        return None


def get_user_info_from_token(token):
    logger.info("get_user_info_from_token view accessed")
    url = settings.USER_INFO_URL
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logger.info("get_user_info_from_token -> User information retrieved successfully")
            user_info = response.json()
            logger.debug(f"get_user_info_from_token -> User info: {user_info}")

            login = user_info.get('login')
            email = user_info.get('email', '')
            first_name = user_info.get('first_name', '')
            last_name = user_info.get('last_name', '')

            logger.debug(f"get_user_info_from_token -> Extracted login: {login}")
            logger.debug(f"get_user_info_from_token -> Extracted email: {email}")
            logger.debug(f"get_user_info_from_token -> Extracted first_name: {first_name}")
            logger.debug(f"get_user_info_from_token -> Extracted last_name: {last_name}")

            return {
                'login': login,
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
        else:
            logger.error(f"Failed to fetch user info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")
        return None


def oauth_callback(request):
    logger.info("OAuth callback accessed")
    code = request.GET.get('code')
    state = request.GET.get('state')
    if not state or state != request.session.get('oauth_state'):
        logger.error("State mismatch or missing")
        return redirect('connexion')
    if not code:
        logger.error("Code missing in request")
        return redirect('connexion')
    token = get_token_from_code(code, state)
    if not token:
        logger.error("Failed to retrieve or decode the token")
        return redirect('connexion')
    user_info = get_user_info_from_token(token)
    if not user_info:
        logger.error("Failed to retrieve user information")
        return redirect('connexion')
    username = user_info.get('login')
    if not username:
        logger.error("Username not found in user information")
        return redirect('connexion')
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_unusable_password()
        user.save()
        logger.info(f"User created: {username}")
    else:
        logger.info(f"Existing user logged in: {username}")

    user.email = user_info.get('email')
    user.first_name = user_info.get('first_name', '')
    user.last_name = user_info.get('last_name', '')
    user.save()

    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.save()

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    logger.info(f"User logged in: {username}")
    return redirect('home')

#########################################################################################################

# Changement mot de passe

def change_password(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('change_password_done')
    else:
        password_form = PasswordChangeForm(request.user)

    context = {
        'password_form': password_form,
    }

    return render(request, 'users/change_password.html', context)


def change_password_done(request):
    return render(request, 'users/change_password_done.html')

#########################################################################################################

# Profil

@login_required
def profile_view(request):
    profile_photos = [settings.MEDIA_URL + f'profile_photos/avatar_{i}.png' for i in range(5)]
    logger.debug("Profile photos paths: %s", profile_photos)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            logger.debug("Form is valid, processing avatar upload.")

            if 'delete_avatar' in request.POST:
                if profile.avatar:
                    if default_storage.exists(profile.avatar.path):
                        default_storage.delete(profile.avatar.path)
                    profile.avatar = None
                    profile.save()
                    messages.success(request, "Avatar supprimé avec succès.")
                    return redirect('profile_view')

            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                logger.debug("Avatar file received: %s", avatar.name)

                image = Image.open(avatar)
                logger.debug("Image opened for resizing.")

                desired_width, desired_height = 1024, 1024
                image = image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
                logger.debug("Image resized to 1024x1024 pixels.")

                temp_thumb = BytesIO()
                image_format = 'PNG' if avatar.name.lower().endswith('.png') else 'JPEG'
                image.save(temp_thumb, image_format)
                temp_thumb.seek(0)
                logger.debug("Image saved to temporary buffer.")

                filename = urllib.parse.quote(avatar.name.replace(" ", "_"))
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploaded_photos'))
                if fs.exists(filename):
                    fs.delete(filename)
                logger.debug("Filesystem storage location set.")

                saved_file = fs.save(filename, ContentFile(temp_thumb.read()))
                temp_thumb.close()
                logger.debug("Resized image saved as: %s", saved_file)

                profile.avatar = 'uploaded_photos/' + saved_file
                logger.debug("Profile avatar path updated to: %s", profile.avatar)
            
            elif 'selected_avatar' in request.POST:
                selected_avatar = request.POST.get('selected_avatar')
                if selected_avatar:
                    profile.avatar = os.path.join('profile_photos', os.path.basename(selected_avatar))
                    logger.info(f"Selected avatar path set to: {profile.avatar}")
                    profile.save()
                    messages.success(request, "Votre profil a été mis à jour avec l'avatar sélectionné.")
                    return redirect('profile_view')

            elif 'avatar' in request.POST:
                selected_avatar = request.POST.get('avatar')
                if selected_avatar:
                    profile.avatar = os.path.join('profile_photos', os.path.basename(selected_avatar))
                    logger.info(f"Selected avatar path set to: {profile.avatar}")
                else:
                    logger.warning("No avatar selected via form")

            profile.save()
            form.save_m2m()
            messages.success(request, "Votre profil a été mis à jour.")
            logger.info("Profile updated successfully and form saved.")
            return redirect('profile_view')
        else:
            messages.error(request, "Il y a des erreurs dans le formulaire.")
            logger.error("Form validation failed with errors: %s", form.errors)

    else:
        form = UserProfileForm(instance=request.user.profile, user=request.user)
        logger.debug("Loaded profile form for user: %s", request.user.username)

    context = {
        'form': form,
        'profile_photos': profile_photos,
    }

    return render(request, 'users/profil.html', context)

#########################################################################################################

# RGPD

@login_required
def deactivate_account(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()

        logger.info(f"Account for user {user.username} has been deactivated.")

        logout(request)

        messages.success(request, "Votre compte a été désactivé avec succès.")
        return redirect('home')
    else:
        return render(request, 'users/deactivate_account.html', {})
    

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        username = user.username

        user.delete()

        logger.info(f"Account for user {username} has been deleted permanently.")

        logout(request)

        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect('home')
    else:
        return render(request, 'users/delete_account.html', {})


@login_required
def anonymize_data(request):
    user = request.user
    if request.method == 'POST':
        user.username = 'anonymous' + get_random_string(8)
        user.email = 'anonymous' + get_random_string(5) + '@example.com'
        user.profile.first_name = ''
        user.profile.last_name = ''
        user.profile.location = ''
        user.profile.bio = None
        user.profile.save()
        user.save()
        messages.success(request, "Vos données ont été anonymisées.")
        return redirect('profile_view')
    return render(request, 'users/anonymize_account.html')


@login_required
def manage_data(request):
    user = request.user
    profile = user.profile

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'users/manage_data.html', context)


def privacy_policy(request):
    return render(request, 'users/privacy_policy.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def secure_view(request):
    return Response({"message": "Hello, you are authenticated!"})

#########################################################################################################

# 2FA

def setup_totp(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        logger.info(f"New user profile created for {user.username}")

    if not hasattr(user, 'totpdevice'):
        device = TOTPDevice.objects.create(user=user, name='default')
        profile.two_factor_enabled = True
        profile.save()
        logger.info(f"2FA activated for user {user.username}")
        url = device.config_url
    else:
        device = user.totpdevice
        url = device.config_url()
        logger.info(f"2FA already configured for user {user.username}")

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'users/setup_totp.html', {'qr_code_url': qr_image_base64, 'user': user})


def verify_totp(request):
    token = request.POST.get('token')
    user = request.user

    if any(device.verify_token(token) for device in devices_for_user(user, confirmed=True)):
        login(request, user)
        logger.info(f"2FA verification successful for user {user.username}")
        return HttpResponse("Connexion réussie avec 2FA")
    else:
        logger.warning(f"Failed 2FA verification attempt for user {user.username}")
        return HttpResponse("Échec de la vérification du token")


@login_required
def disable_2fa(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.two_factor_enabled:
        user_profile.two_factor_enabled = False
        user_profile.save()
        messages.success(request, "2FA has been disabled successfully.")
        logger.info(f"2FA disabled for user {request.user.username}")
    else:
        messages.info(request, "2FA is not enabled on your account.")
        logger.info(f"Attempt to disable 2FA but it was not enabled for user {request.user.username}")
    return redirect('profile_view')

#########################################################################################################

# friends

@login_required
def friends_list(request):
    current_user = request.user
    current_user_profile = current_user.profile

    if request.method == 'POST':
        if 'add' in request.POST:
            friend_id = request.POST.get('add')
            friend_profile = UserProfile.objects.get(pk=friend_id)
            current_user_profile.friends.add(friend_profile)
        elif 'remove' in request.POST:
            friend_id = request.POST.get('remove')
            friend_profile = UserProfile.objects.get(pk=friend_id)
            current_user_profile.friends.remove(friend_profile)

    current_user_profile.refresh_from_db()
    friends_profiles = current_user_profile.friends.all()
    friends_user_ids = [profile.user.id for profile in friends_profiles]

    non_friends = User.objects.exclude(id__in=friends_user_ids).exclude(id=current_user.id)
    
    return render(request, 'users/friends.html', {
        'friends': friends_profiles,
        'non_friends': non_friends
    })


@login_required
def add_friend(request, friend_id):
    user_profile = request.user.profile
    friend_profile = UserProfile.objects.get(pk=friend_id)
    user_profile.friends.add(friend_profile)
    return redirect('friends_list')


@login_required
def remove_friend(request, friend_id):
    user_profile = request.user.profile
    friend_profile = UserProfile.objects.get(pk=friend_id)
    user_profile.friends.remove(friend_profile)
    return redirect('friends_list')


@login_required
def friend_status_api(request):
    current_user = request.user
    friends = current_user.profile.friends.prefetch_related('user').all()

    result = {
        'friends': [
            {
                'username': friend.user.username,
                'status': friend.status
            } for friend in friends
        ]
    }

    return JsonResponse(result)

#########################################################################################################

# Statistiques

@login_required
def view_statistics(request):
    logger.info("Accès à la vue des statistiques par l'utilisateur %s", request.user.username)
    
    current_user = request.user
    user_profile = UserProfile.objects.get(user=current_user)
    friends_profiles = user_profile.friends.all()

    # Fonction pour calculer le ratio victoires/défaites en pourcentage
    def win_loss_ratio(wins, losses):
        total_games = wins + losses
        return (wins / total_games * 100) if total_games > 0 else 0

    # Récupération des statistiques par type de jeu
    def get_pong_stats(user, game_type):
        games_won = Game.objects.filter(Q(player1=user) & Q(winner=user) & Q(game_type=game_type)).count() + \
                    Game.objects.filter(Q(player2=user) & Q(winner=user) & Q(game_type=game_type)).count()
        games_lost = Game.objects.filter(Q(player1=user) & ~Q(winner=user) & Q(game_type=game_type)).count() + \
                     Game.objects.filter(Q(player2=user) & ~Q(winner=user) & Q(game_type=game_type)).count()
        total_games = games_won + games_lost
        return {
            'total_wins': games_won,
            'total_losses': games_lost,
            'total_games': total_games,
            'win_loss_ratio': win_loss_ratio(games_won, games_lost)
        }

    def get_invaders_stats(user):
        invader_games = InvadersPlayer.objects.filter(player=user).order_by('-game__game_date')
        total_games = invader_games.count()
        last_score = invader_games.first().score if invader_games.exists() else 0
        best_score = invader_games.aggregate(max_score=Max('score'))['max_score'] or 0
        avg_score = invader_games.aggregate(avg_score=Avg('score'))['avg_score'] or 0
        return {
            'total_games': total_games,
            'last_score': last_score,
            'best_score': best_score,
            'avg_score': avg_score
        }

    # Statistiques de l'utilisateur courant
    user_stats = {
        'pong2d': get_pong_stats(current_user, 'pong2d'),
        'invaders': get_invaders_stats(current_user),
    }

    # Récupération des statistiques des amis
    friends_stats = []
    for friend in friends_profiles:
        friend_stats = {
            'username': friend.user.username,
            'pong2d': get_pong_stats(friend.user, 'pong2d'),
            'invaders': get_invaders_stats(friend.user),
        }
        friends_stats.append(friend_stats)

    context = {
        'user_profile': user_profile,
        'user_stats': user_stats,
        'friends_stats': friends_stats,
    }

    logger.info("Contexte pour view_statistics: %s", context)
    return render(request, 'users/statistics.html', context)

#########################################################################################################


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from users.models import UserProfile, Game
from invaders.models import Player as InvadersPlayer
import logging

logger = logging.getLogger(__name__)

@login_required
def game_history(request):
    logger.info("Accès à la vue game_history par l'utilisateur %s", request.user.username)

    user = request.user

    # Récupération des jeux Pong 2D (player vs player, player vs IA, tournoi)
    pong2d_games_pvp = Game.objects.filter(
        Q(player1=user) | Q(player2=user),
        game_type='pong2d',
        is_vs_ai=False,
        tournament__isnull=True
    ).order_by('-game_date')

    pong2d_games_vs_ai = Game.objects.filter(
        player1=user,
        game_type='pong2d',
        is_vs_ai=True
    ).order_by('-game_date')

    pong2d_tournament_games = Game.objects.filter(
        Q(player1=user) | Q(player2=user),
        game_type='pong2d',
        tournament__isnull=False
    ).order_by('-game_date')

    # Récupération des jeux Pong API 2D (player vs player, player vs IA, tournoi)
    pongapi2d_games_pvp = Game.objects.filter(
        Q(player1=user) | Q(player2=user),
        game_type='pongapi2d',
        is_vs_ai=False,
        tournament__isnull=True
    ).order_by('-game_date')

    pongapi2d_games_vs_ai = Game.objects.filter(
        player1=user,
        game_type='pongapi2d',
        is_vs_ai=True
    ).order_by('-game_date')

    pongapi2d_tournament_games = Game.objects.filter(
        Q(player1=user) | Q(player2=user),
        game_type='pongapi2d',
        tournament__isnull=False
    ).order_by('-game_date')

    # Récupération des jeux Pong AI (player vs player, player vs IA, tournoi)
    pong_ai_games_pvp = Game.objects.filter(
        Q(player1=user) | Q(player2=user),
        game_type='pong_ai',
        is_vs_ai=False,
        tournament__isnull=True
    ).order_by('-game_date')

    pong_ai_games_vs_ai = Game.objects.filter(
        player1=user,
        game_type='pong_ai',
        is_vs_ai=True
    ).order_by('-game_date')

    pong_ai_tournament_games = Game.objects.filter(
        Q(player1=user) | Q(player2=user),
        game_type='pong_ai',
        tournament__isnull=False
    ).order_by('-game_date')

    # Récupération des jeux Invaders (solo, tournoi)
    invaders_players = InvadersPlayer.objects.filter(player=user).order_by('-game__game_date')

    invaders_tournament_games = Game.objects.filter(
        Q(player1=user) | Q(player2=user),
        game_type='invaders',
        tournament__isnull=False
    ).order_by('-game_date')

    context = {
        'pong2d_games_pvp': pong2d_games_pvp,
        'pong2d_games_vs_ai': pong2d_games_vs_ai,
        'pong2d_tournament_games': pong2d_tournament_games,
        'pongapi2d_games_pvp': pongapi2d_games_pvp,
        'pongapi2d_games_vs_ai': pongapi2d_games_vs_ai,
        'pongapi2d_tournament_games': pongapi2d_tournament_games,
        'pong_ai_games_pvp': pong_ai_games_pvp,
        'pong_ai_games_vs_ai': pong_ai_games_vs_ai,
        'pong_ai_tournament_games': pong_ai_tournament_games,
        'invaders_players': invaders_players,
        'invaders_tournament_games': invaders_tournament_games,
    }

    logger.info("Contexte pour game_history : %s", context)
    return render(request, 'users/game_history.html', context)




#########################################################################################################

# Generation token

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

class ObtainTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"error": "Invalid credentials"}, status=400)

#########################################################################################################

