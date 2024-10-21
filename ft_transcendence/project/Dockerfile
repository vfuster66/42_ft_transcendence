# Utilisation de l'image Python 3.10.12 officielle
FROM python:3.10.12

# Définition du répertoire de travail dans le conteneur
WORKDIR /project/

# Installation des dépendances nécessaires
RUN apt-get update \
    && apt-get install -y postgresql-client netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copie du fichier des exigences (requirements.txt) dans le conteneur
COPY requirements.txt .

# Installation des dépendances Python à partir du fichier requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie du script de migration dans le conteneur
COPY migrate.sh .

# Attribution des permissions d'exécution au script de migration
RUN chmod +x migrate.sh

# Copie du reste des fichiers du projet dans le conteneur
COPY . .

# Commande par défaut pour exécuter le script de migration
CMD ["./migrate.sh"]

