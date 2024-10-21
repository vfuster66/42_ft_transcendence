
# users/middleware.py

#########################################################################################################

from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.contrib.auth.models import User
from users.models import UserProfile

#########################################################################################################

class UpdateUserStatusMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'profile'):
                UserProfile.objects.create(user=request.user, display_name=request.user.username)

            current_url = resolve(request.path_info).url_name
            if current_url in ['pongapi2d_pvp', 'pongapi2d_ia', 'game3d', 'invaders', 'pong2d_ia', 'pong2d_pvp']:
                request.user.profile.status = 'IN_GAME'
            elif request.user.profile.status == 'IN_GAME':
                request.user.profile.status = 'ONLINE'
            request.user.profile.save()
        return None

#########################################################################################################

import uuid
import logging
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()
logger = logging.getLogger(__name__)

class TabSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tab_id = request.COOKIES.get('tab_id')
        if tab_id:
            user_id = request.session.get(f'user_id_{tab_id}')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    request.user = user
                    logger.debug(f"User {user.username} authenticated with tab_id={tab_id}")
                except User.DoesNotExist:
                    request.user = None
                    logger.error(f"User with id={user_id} does not exist")
            else:
                request.user = None
                logger.debug(f"No user_id found for tab_id={tab_id}")
        else:
            request.user = None
            logger.debug("No tab_id found in cookies")

    def process_response(self, request, response):
        tab_id = request.COOKIES.get('tab_id')
        if not tab_id:
            tab_id = str(uuid.uuid4())
            response.set_cookie('tab_id', tab_id)
            logger.debug(f"Set new tab_id={tab_id} in cookies")
        else:
            response.set_cookie('tab_id', tab_id)
            logger.debug(f"Set tab_id={tab_id} in cookies")
        return response














