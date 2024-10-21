#!/bin/bash
set -e

# Attendre que la base de données PostgreSQL soit prête
while ! nc -z postgres 5432; do
  echo "Attente du démarrage de la base de données PostgreSQL..."
  sleep 1
done

# Définir la variable d'environnement DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE=project.settings

# Exécuter les migrations
python manage.py makemigrations
python manage.py migrate

# Collecter les fichiers statiques pour admin
python manage.py collectstatic --skip-checks --noinput

# Créer un superutilisateur automatiquement, si nécessaire
python manage.py shell < superuser.py
python manage.py shell < createuser.py

# Démarrer Daphne
daphne -b 0.0.0.0 -p ${DJANGO_PORT} project.asgi:application
