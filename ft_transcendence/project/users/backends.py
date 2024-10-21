
# users/backends.py

#########################################################################################################

from social_core.backends.oauth import BaseOAuth2

import os

#########################################################################################################

class FortyTwoOAuth2(BaseOAuth2):
    name = 'fortytwo'
    AUTHORIZATION_URL = os.getenv('OAUTH_AUTHORIZE_URL')
    ACCESS_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    DEFAULT_SCOPE = ['public', 'profile']
    REDIRECT_URI = os.getenv('REDIRECT_42')
    EXTRA_DATA = [
        ('email', 'email'),
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
    ]

#########################################################################################################

