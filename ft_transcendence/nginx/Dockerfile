FROM nginx:latest

# Copiez votre configuration Nginx personnalisée
COPY ./conf/default /etc/nginx/conf.d/default.conf

# Copiez et attribuez les bonnes permissions au script de démarrage
COPY ./tools/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 443

CMD ["/start.sh"]

