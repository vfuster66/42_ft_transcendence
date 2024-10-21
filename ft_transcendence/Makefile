# Chemin vers le fichier docker-compose.yml
DC = docker-compose.yml

# Chemin vers les scripts de migration et de génération de certificats
MIGRATE_SCRIPT = project/migrate.sh

.PHONY: all build up down clean fclean re refclean check-perms set-script-perms

all: check-perms build up

check-perms:
	@if [ ! -x $(MIGRATE_SCRIPT) ]; then \
		echo "Migrate.sh n'a pas les permissions adéquates. Mise à jour en cours..."; \
		chmod +x $(MIGRATE_SCRIPT); \
	else \
		echo "Migrate.sh a déjà les permissions nécessaires."; \
	fi

build:
	@echo "Building containers..."
	mkdir -p volumes/pg_data
	docker-compose -f $(DC) build

up:
	@echo "Starting containers..."
	docker-compose -f $(DC) up -d

down:
	@echo "Stopping containers..."
	docker-compose -f $(DC) down

restart-nginx:
	@echo "Rebuilding and restarting nginx service..."
	docker-compose -f $(DC) stop nginx
	docker-compose -f $(DC) rm -f nginx
	docker-compose -f $(DC) up -d --no-deps --build nginx

restart-postgres:
	@echo "Rebuilding and restarting postgres service..."
	docker-compose -f $(DC) stop postgres
	docker-compose -f $(DC) rm -f postgres
	docker-compose -f $(DC) up -d --no-deps --build postgres

restart-pgadmin:
	@echo "Rebuilding and restarting pgadmin service..."
	docker-compose -f $(DC) stop pgadmin
	docker-compose -f $(DC) rm -f pgadmin
	docker-compose -f $(DC) up -d --no-deps --build pgadmin

restart-back:
	@echo "Rebuilding and restarting back service..."
	docker-compose -f $(DC) stop back
	docker-compose -f $(DC) rm -f back
	docker-compose -f $(DC) up -d --no-deps --build back

restart-elasticsearch:
	@echo "Rebuilding and restarting elasticsearch service..."
	docker-compose -f $(DC) stop elasticsearch
	docker-compose -f $(DC) rm -f elasticsearch
	docker-compose -f $(DC) up -d --no-deps --build elasticsearch

restart-kibana:
	@echo "Rebuilding and restarting kibana service..."
	docker-compose -f $(DC) stop kibana
	docker-compose -f $(DC) rm -f kibana
	docker-compose -f $(DC) up -d --no-deps --build kibana

restart-logstash:
	@echo "Rebuilding and restarting logstash service..."
	docker-compose -f $(DC) stop logstash
	docker-compose -f $(DC) rm -f logstash
	docker-compose -f $(DC) up -d --no-deps --build logstash

clean:
	@echo "Cleaning up..."
	docker-compose -f $(DC) down
	docker volume prune -f
	docker network prune -f

fclean: check-ports
	@echo "Forcing clean..."
	docker-compose -f $(DC) down -v
	docker system prune --all -f --volumes

re: down up

refclean: fclean up

check-ports:
	@echo "Checking ports..."
	@! lsof -i :5432 | grep LISTEN || (echo "Port 5432 is still in use" && exit 1)
	@! lsof -i :8000 | grep LISTEN || (echo "Port 8000 is still in use" && exit 1)
	@! lsof -i :80 | grep LISTEN || (echo "Port 80 is still in use" && exit 1)
