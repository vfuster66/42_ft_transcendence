import os
import django
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')
django.setup()

from django.contrib.auth.models import User

# Liste des utilisateurs à créer
users = [
    {'username': os.getenv('USER_1'), 'password': os.getenv('USER_PASSWORD_1'), 'email': os.getenv('USER_EMAIL_1')},
    {'username': os.getenv('USER_2'), 'password': os.getenv('USER_PASSWORD_2'), 'email': os.getenv('USER_EMAIL_2')},
    {'username': os.getenv('USER_3'), 'password': os.getenv('USER_PASSWORD_3'), 'email': os.getenv('USER_EMAIL_3')},
    {'username': os.getenv('USER_4'), 'password': os.getenv('USER_PASSWORD_4'), 'email': os.getenv('USER_EMAIL_4')},
    {'username': os.getenv('USER_5'), 'password': os.getenv('USER_PASSWORD_5'), 'email': os.getenv('USER_EMAIL_5')},
    {'username': os.getenv('USER_6'), 'password': os.getenv('USER_PASSWORD_6'), 'email': os.getenv('USER_EMAIL_6')},
    {'username': os.getenv('USER_7'), 'password': os.getenv('USER_PASSWORD_7'), 'email': os.getenv('USER_EMAIL_7')},
    {'username': os.getenv('USER_8'), 'password': os.getenv('USER_PASSWORD_8'), 'email': os.getenv('USER_EMAIL_8')},
]

# Création des utilisateurs
for user_data in users:
    if not User.objects.filter(username=user_data['username']).exists():
        User.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email']
        )
        print(f"Utilisateur {user_data['username']} créé.")
    else:
        print(f"Utilisateur {user_data['username']} existe déjà.")

print("Création des utilisateurs terminée.")
