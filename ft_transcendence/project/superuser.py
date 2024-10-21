import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Super utilisateur existant
username = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
email = os.environ.get('POSTGRES_EMAIL')

if username and password and email and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superutilisateur {username} créé.")
else:
    print(f"Superutilisateur {username} existe déjà ou informations manquantes.")

# Nouveaux super utilisateurs
superusers = [
    ('SUPERUSER_1', 'SUPERUSER_PASSWORD_1', 'SUPERUSER_EMAIL_1'),
    ('SUPERUSER_2', 'SUPERUSER_PASSWORD_2', 'SUPERUSER_EMAIL_2'),
    ('SUPERUSER_3', 'SUPERUSER_PASSWORD_3', 'SUPERUSER_EMAIL_3')
]

for user_env, pass_env, email_env in superusers:
    new_username = os.environ.get(user_env)
    new_password = os.environ.get(pass_env)
    new_email = os.environ.get(email_env)
    if new_username and new_password and new_email and not User.objects.filter(username=new_username).exists():
        User.objects.create_superuser(new_username, new_email, new_password)
        print(f"Superutilisateur {new_username} créé.")
    else:
        print(f"Superutilisateur {new_username} existe déjà ou informations manquantes.")

print("Création des superutilisateurs terminée.")
