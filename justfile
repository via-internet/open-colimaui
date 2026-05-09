set shell := ["bash", "-cu"]

export COMPOSE_PROJECT_NAME := "opendockerwebui"

FRONTEND_URL := "http://localhost:5173"
BACKEND_URL := "http://localhost:8000"

default:
    @just --list

up:
    docker compose up --build

up-d:
    docker compose up --build -d

down:
    docker compose down

restart:
    docker compose down
    docker compose up --build

rebuild:
    docker compose build --no-cache

reset:
    docker compose down -v --remove-orphans
    docker compose up --build

clean:
    docker compose down -v --remove-orphans
    docker system prune -f

nuke:
    docker compose down -v --remove-orphans
    docker system prune -af
    docker volume prune -f

logs:
    docker compose logs -f

backend-logs:
    docker compose logs -f backend

frontend-logs:
    docker compose logs -f frontend

logs-tail:
    docker compose logs --tail=100 -f

backend-shell:
    docker compose exec backend bash

frontend-shell:
    docker compose exec frontend sh

backend-root-shell:
    docker compose exec -u root backend bash

ps:
    docker compose ps

top:
    docker compose top

stats:
    docker stats

images:
    docker images

volumes:
    docker volume ls

networks:
    docker network ls

api-health:
    curl -s {{BACKEND_URL}}/health | python -m json.tool

api-info:
    curl -s {{BACKEND_URL}}/docker/info | python -m json.tool

api-containers:
    curl -s {{BACKEND_URL}}/docker/containers | python -m json.tool

api-images:
    curl -s {{BACKEND_URL}}/docker/images | python -m json.tool

open-frontend:
    open {{FRONTEND_URL}}

open-backend:
    open {{BACKEND_URL}}

open-api-docs:
    open {{BACKEND_URL}}/docs

frontend-install:
    docker compose exec frontend npm install

frontend-build:
    docker compose exec frontend npm run build

backend-pip-list:
    docker compose exec backend pip list

backend-routes:
    curl -s {{BACKEND_URL}}/openapi.json | python -m json.tool

docker-version:
    docker version

docker-info:
    docker info

docker-context:
    docker context ls

docker-socket:
    ls -lah /var/run/docker.sock

health:
    @echo "Frontend:"
    @curl -I {{FRONTEND_URL}} || true
    @echo ""
    @echo "Backend:"
    @curl -I {{BACKEND_URL}} || true

urls:
    @echo ""
    @echo "Frontend : {{FRONTEND_URL}}"
    @echo "Backend  : {{BACKEND_URL}}"
    @echo "Swagger  : {{BACKEND_URL}}/docs"
    @echo ""

tree:
    tree -I 'node_modules|dist|__pycache__|.git'

config:
    docker compose config

validate:
    docker compose config --quiet

stop:
    docker compose stop

start:
    docker compose start

rm:
    docker compose rm -f

prune-images:
    docker image prune -f

prune-volumes:
    docker volume prune -f

prune-networks:
    docker network prune -f
