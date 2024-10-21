
# project/urls.py

#########################################################################################################

from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from tournaments.views import (
    tournament_update_game, tournament_details, create_tournament, tournament_pong2d_pvp,
    pong2d_tournament_match_end, matchmaking, tournament_api_details, tournament_api_update_game, 
    tournament_pongapi2d_pvp, pongapi2d_tournament_match_end, create_api_tournament, matchmaking_api
)
from invaders.views import (
    invaders_win, invaders_lose, create_invaders_tournament,
    invaders_tournament_details, invaders_match_end, select_mode, invaders_solo, 
    invaders_tournament
)
from pong2d.views import (
    pong2d_mode, pong2d_pvp, pong2d_ia, pong2d_choose, pong2d_failure, pong2d_success, pong2d_pvp_success,
    pong2d_match_end, pong2d_ia_end_match
)
from pongapi2d.views import (
    GameViewSet, AIGameViewSet, pongapi2d_choose, pongapi2d_pvp, pongapi2d_ia, pongapi2d_failure,
    pongapi2d_mode, pongapi2d_pvp_success, pongapi2d_success, pongapi2d_match_end
)
from chat.views import (
    room_detail, room_list, create_room, access_denied_view, block_user,unblock_user, get_user_profile
)
from pong3d.views import game3D, get_player_info, post_game_results

from users.views import (
    base, home, signup, connexion, logout_view, logout_message, privacy_policy,
    secure_view, view_statistics, game_history,
    profile_view, change_password, change_password_done, deactivate_account, delete_account, anonymize_data, manage_data,
    friends_list, add_friend, remove_friend, oauth_callback, start_oauth, CustomLoginView, 
    setup_totp, disable_2fa, ObtainTokenView, GameViewSet, UserProfileViewSet
)
from django.conf.urls.static import static
from django.conf import settings
from django.views.i18n import set_language

from .views import environment_variables_view

#########################################################################################################

router = DefaultRouter()
router.register(r'ai_games', AIGameViewSet)
router.register(r'users', UserProfileViewSet)
router.register(r'games', GameViewSet, basename='game')

#########################################################################################################

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', base, name='base'),
    path('env-vars/', environment_variables_view, name='environment_variables'),
    path('home/', home, name='home'),
    path('signup/', signup, name='signup'),
    path('connexion/', connexion, name='connexion'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('logout_message/', logout_message, name='logout_message'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('oauth-callback', oauth_callback, name='oauth-callback'),
    # path('complete/fortytwo/', oauth_callback, name='oauth_callback'),
    path('start-oauth/', start_oauth, name='start_oauth'),
    path('profile/', profile_view, name='profile_view'),
    path('change_password/', change_password, name='change_password'),
    path('change_password_done/', change_password_done, name='change_password_done'),
    path('deactivate_account/', deactivate_account, name='deactivate_account'),
    path('delete_account/', delete_account, name='delete_account'),
    path('anonymize_data/', anonymize_data, name='anonymize_data'),
    path('manage_data/', manage_data, name='manage_data'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/token/obtain/', ObtainTokenView.as_view(), name='token_obtain'),
    path('secure-endpoint/', secure_view, name='secure-endpoint'),
    path('setup-totp/', setup_totp, name='setup_totp'),
    path('disable-2fa/', disable_2fa, name='disable_2fa'),
    path('friends/', friends_list, name='friends_list'),
    path('add_friend/<int:friend_id>/', add_friend, name='add_friend'),
    path('remove_friend/<int:friend_id>/', remove_friend, name='remove_friend'),
    path('statistics/', view_statistics, name='view_statistics'),
    path('game_history/', game_history, name='game_history'),
    path('set_language/', set_language, name='set_language'),
    path('rooms/', room_list, name='room_list'),
    path('rooms/create/', create_room, name='create_room'),
    path('rooms/<str:room_name>/', room_detail, name='room_detail'),
    path('access-denied/', access_denied_view, name='access_denied_view'),
    path('block/<int:user_id>/', block_user, name='block_user'),
    path('unblock/<int:user_id>/', unblock_user, name='unblock_user'),
    path('get-user-profile/', get_user_profile, name='get_user_profile'),
    path('get_player_info/', get_player_info, name='get_player_info'),
    path('post_game_results/', post_game_results, name='post_game_results'),
    path('game3D/', game3D, name='game3D'),

    path('pongapi2d_mode/', pongapi2d_mode, name='pongapi2d_mode'),
    path('pongapi2d_choose/', pongapi2d_choose, name='pongapi2d_choose'),
    path('pongapi2d_pvp/<int:player1_id>/<int:player2_id>/', pongapi2d_pvp, name='pongapi2d_pvp'),
    path('tournament_pongapi2d_pvp/<int:player1_id>/<int:player2_id>/', tournament_pongapi2d_pvp, name='tournament_pongapi2d_pvp'),
    path('pongapi2d_ia/', pongapi2d_ia, name='pongapi2d_ia'),
    path('pongapi2d_success/', pongapi2d_success, name='pongapi2d_success'),
    path('pongapi2d_failure/', pongapi2d_failure, name='pongapi2d_failure'),
    path('pongapi2d_pvp_success/', pongapi2d_pvp_success, name='pongapi2d_pvp_success'),
    path('pongapi2d_match_end/', pongapi2d_match_end, name='pongapi2d_match_end'),

    path('pong2d_mode/', pong2d_mode, name='pong2d_mode'),
    path('pong2d_choose/', pong2d_choose, name='pong2d_choose'),
    path('pong2d_pvp/<int:player1_id>/<int:player2_id>/', pong2d_pvp, name='pong2d_pvp'),
    path('tournament_pong2d_pvp/<int:player1_id>/<int:player2_id>/', tournament_pong2d_pvp, name='tournament_pong2d_pvp'),
    path('pong2d_ia/', pong2d_ia, name='pong2d_ia'),
    path('pong2d_success/', pong2d_success, name='pong2d_success'),
    path('pong2d_failure/', pong2d_failure, name='pong2d_failure'),
    path('pong2d_pvp_success/', pong2d_pvp_success, name='pong2d_pvp_success'),
    path('pong2d_match_end/', pong2d_match_end, name='pong2d_match_end'),
    path('pong2d_ia_end_match/', pong2d_ia_end_match, name='pong2d_ia_end_match'),

    path('invaders_solo/', invaders_solo, name='invaders_solo'),
    path('invaders_tournament/', invaders_tournament, name='invaders_tournament'),
    path('select_mode/', select_mode, name='select_mode'),
    path('invaders_win/', invaders_win, name='invaders_win'),
    path('invaders_lose/', invaders_lose, name='invaders_lose'),
    path('create_invaders_tournament/', create_invaders_tournament, name='create_invaders_tournament'),
    path('invaders_tournament_details/<int:tournament_id>/', invaders_tournament_details, name='invaders_tournament_details'),
    path('invaders_match_end/', invaders_match_end, name='invaders_match_end'),

    path('create_tournament/', create_tournament, name='create_tournament'),
    path('tournament_details/<int:tournament_id>/', tournament_details, name='tournament_details'),
    path('tournament_update_game/<int:game_id>/', tournament_update_game, name='tournament_update_game'),
    path('matchmaking/', matchmaking, name='matchmaking'),
    path('tournament_pong2d_pvp/<int:player1_id>/<int:player2_id>/<int:tournament_id>/<int:match_id>/', tournament_pong2d_pvp, name='tournament_pong2d_pvp'),
    path('pong2d_tournament_match_end/', pong2d_tournament_match_end, name='pong2d_tournament_match_end'),

    path('tournament_pongapi2d_pvp/<int:player1_id>/<int:player2_id>/<int:tournament_id>/<int:match_id>/', tournament_pongapi2d_pvp, name='tournament_pongapi2d_pvp'),
    path('create_api_tournament/', create_api_tournament, name='create_api_tournament'),
    path('matchmaking_api/', matchmaking_api, name='matchmaking_api'),
    path('tournament_api_details/<int:tournament_id>/', tournament_api_details, name='tournament_api_details'),
    path('tournament_api_update_game/<int:game_id>/', tournament_api_update_game, name='tournament_api_update_game'),
    path('pongapi2d_tournament_match_end/', pongapi2d_tournament_match_end, name='pongapi2d_tournament_match_end'),
]

#########################################################################################################

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


#########################################################################################################

