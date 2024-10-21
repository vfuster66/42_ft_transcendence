#!/bin/bash

# Création des répertoires pour les certificats SSL
echo "Nginx: setting up directories for SSL..."
mkdir -p /etc/ssl/certs /etc/ssl/private

# Utiliser les certificats fournis si présents
if [ -f /etc/ssl/certs/pandapong.pem ] && [ -f /etc/ssl/private/pandapong.key ]; then
    echo "Nginx: using provided SSL certificate and key..."
    chmod 600 /etc/ssl/private/pandapong.key
else
    echo "Nginx: No valid SSL certificate found, please check paths and files."
    exit 1  # Arrête le script si aucun certificat n'est trouvé
fi

# Démarrage de Nginx en mode foreground
echo "Nginx: starting..."
nginx -g "daemon off;"
