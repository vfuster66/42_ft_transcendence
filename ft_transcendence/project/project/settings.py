
# project/settings.py

#########################################################################################################

import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from datetime import timedelta

#########################################################################################################

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'file': {
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': os.path.join('/project/logs', 'all_logs.log'),
			'formatter': 'verbose',
		},
		'console': {
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'formatter': 'simple'
		},
	},
	'formatters': {
		'verbose': {
			'format': '{levelname} {asctime} {module} {message}',
			'style': '{',
		},
		'simple': {
			'format': '{levelname} {message}',
			'style': '{',
		},
	},
	'root': {
		'handlers': ['file', 'console'],
		'level': 'DEBUG',
	},
}

#########################################################################################################

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"La variable d'environnement {var_name} n'a pas été définie."
        raise ImproperlyConfigured(error_msg)


# Définir les variables d'environnement
POSTGRES_USER = os.getenv('POSTGRES_USER', 'default_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'default_password')

# Ajouter ces variables aux settings de Django
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# Définition du répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Récupération de la clé secrète Django depuis les variables d'environnement
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

#########################################################################################################

# Récupération des identifiants pour l'authentification 42 depuis les variables d'environnement

UID = os.getenv("UID")
SECRET = os.getenv("SECRET")
NEXT_SECRET = os.getenv("NEXT_SECRET")
OAUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')
OAUTH_AUTHORIZE_URL = os.getenv('OAUTH_AUTHORIZE_URL')
REDIRECT_URI = os.getenv("REDIRECT_URI")
USER_INFO_URL = os.getenv('USER_INFO_URL')

# Configuration des identifiants 42 pour l'authentification sociale

SOCIAL_AUTH_42_KEY = UID
SOCIAL_AUTH_42_SECRET = SECRET
NEXT_SOCIAL_AUTH_42_SECRET = NEXT_SECRET
SOCIAL_AUTH_42_REDIRECT_URI = REDIRECT_URI

#########################################################################################################

# Activation du mode de débogage

DEBUG = True

#########################################################################################################

# Liste des hôtes autorisés

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS').split(',')

#########################################################################################################

# Identifiant du site

SITE_ID = 1

#########################################################################################################

# Liste des applications installées dans le projet Django

INSTALLED_APPS = [
		'users.apps.UsersConfig',
		'django.contrib.admin',
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'django.contrib.sites',
		'allauth',
		'allauth.account',
		'social_django',
		'pong3d',
		'widget_tweaks',
		'django_otp',
		'django_otp.plugins.otp_static',
		'django_otp.plugins.otp_totp',
		'formtools',
		'channels',
		'chat',
		'corsheaders',
		'rest_framework',
		'django_extensions',
		'pongapi2d',
		'pong2d',
		'invaders',
		'tournaments',
]

#########################################################################################################

ASGI_APPLICATION = 'project.asgi.application'

#########################################################################################################

# Configuration Redis

REDIS_HOST = get_env_variable('REDIS_HOST')
REDIS_PORT = int(get_env_variable('REDIS_PORT'))
REDIS_DB = int(get_env_variable('REDIS_DB'))

#########################################################################################################

# Configuration des canaux pour les connexions WebSocket

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

#########################################################################################################

# Listes des classes utilisées pour l'authentification

AUTHENTICATION_BACKENDS = (
	# Backend d'authentification par défaut de Django
	'django.contrib.auth.backends.ModelBackend',
	# Backend d'authentification pour les comptes Allauth
	'allauth.account.auth_backends.AuthenticationBackend',
	# Backend d'authentification personnalisé pour l'authentification 42
	'users.backends.FortyTwoOAuth2',
)

#########################################################################################################

# Middleware utilisés par Django

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'users.middleware.TabSessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'allauth.account.middleware.AccountMiddleware',
	'social_django.middleware.SocialAuthExceptionMiddleware',
	'django_otp.middleware.OTPMiddleware',
	'django.middleware.locale.LocaleMiddleware',
    'users.middleware.UpdateUserStatusMiddleware',

]

CORS_ALLOW_ALL_ORIGINS = True


# Middleware personnalisé pour définir le type de contenu des fichiers CSS
class CssMiddleware(MiddlewareMixin):
	def process_response(self, request, response):
		if request.path.endswith('.css'):
			response['Content-Type'] = 'text/css'
		return response


# Middleware pour la gestion des exceptions
class ExceptionHandlingMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		return response

	def process_exception(self, request, exception):
		return JsonResponse({'status': 'error', 'message': 'An internal error occurred'}, status=500)

#########################################################################################################

# Configuration de l'URL racine de l'application

ROOT_URLCONF = 'project.urls'

#########################################################################################################

# Configuration des templates utilisés par l'application

TEMPLATES = [
		{
				'BACKEND': 'django.template.backends.django.DjangoTemplates',
				'DIRS': [BASE_DIR / 'templates'],
				'APP_DIRS': True,
				'OPTIONS': {
						'context_processors': [
								'django.template.context_processors.debug',
								'django.template.context_processors.request',
								'django.contrib.auth.context_processors.auth',
								'django.contrib.messages.context_processors.messages',
								'django.template.context_processors.media',
								],
						},
				},
]

#########################################################################################################

# Configuration de l'application WSGI

WSGI_APPLICATION = 'project.wsgi.application'

#########################################################################################################

# Configuration de la base de données PostgreSQL

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ['POSTGRES_NAME'],
		'USER': os.environ['POSTGRES_USER'],
		'PASSWORD': os.environ['POSTGRES_PASSWORD'],
		'HOST': os.environ['POSTGRES_HOST'],
		'PORT': os.environ['POSTGRES_PORT'],
	}
}

#########################################################################################################

# Configuration des validateurs de mots de passe

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'users.validators.CustomPasswordValidator',
	},
]

#########################################################################################################

# Configuration des langues et des traductions

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
LANGUAGES = [
	('en', 'English'),
	('fr', 'French'),
	('es', 'Spanish'),
]
LOCALE_PATHS = (
	os.path.join(BASE_DIR, 'locale'),
)

#########################################################################################################

# Configuration du fuseau horaire

TIME_ZONE = 'Europe/Paris'
USE_TZ = True

#########################################################################################################

# Configuration des fichiers statiques

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

#########################################################################################################

# Configuration du champ par défaut pour les clés primaires

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#########################################################################################################

# URL de redirection pour l'authentification

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

#########################################################################################################

# Configuration des fichiers média

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#########################################################################################################

# Configuration du framework REST

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	),
}

#########################################################################################################
# Configuration du module JWT simple

SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
	'ROTATE_REFRESH_TOKENS': True,
	'BLACKLIST_AFTER_ROTATION': True,

	'ALGORITHM': 'HS256',
	'SIGNING_KEY': SECRET_KEY,
	'VERIFYING_KEY': None,
	'AUDIENCE': None,
	'ISSUER': None,
	
	'AUTH_HEADER_TYPES': ('Bearer',),
	'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
	'USER_ID_FIELD': 'id',
	'USER_ID_CLAIM': 'user_id',
	
	'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
	'TOKEN_TYPE_CLAIM': 'token_type',
}

#########################################################################################################

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

#########################################################################################################

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

