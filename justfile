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

backend-container:
    docker compose up --build backend

frontend-local:
    cd frontend && npm install && npm run dev -- --host 0.0.0.0

dev-backend-container:
    docker compose up --build -d backend
    cd frontend && npm install && npm run dev -- --host 0.0.0.0

frontend-container:
    docker compose up --build frontend

backend-local:
    cd backend && python -m venv .venv
    cd backend && source .venv/bin/activate && pip install -r requirements.txt
    cd backend && source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend-container:
    docker compose up --build -d frontend
    cd backend && python -m venv .venv
    cd backend && source .venv/bin/activate && pip install -r requirements.txt
    cd backend && source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev-local:
    cd backend && python -m venv .venv
    cd backend && source .venv/bin/activate && pip install -r requirements.txt
    cd backend && source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload & \
    cd frontend && npm install && npm run dev -- --host 0.0.0.0

down:
    docker compose down

stop:
    docker compose stop

start:
    docker compose start

restart:
    docker compose down
    docker compose up --build

restart-d:
    docker compose down
    docker compose up --build -d

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

ps:
    docker compose ps

stats:
    docker stats

api-health:
    curl -s {{BACKEND_URL}}/health | python -m json.tool

api-info:
    curl -s {{BACKEND_URL}}/docker/info | python -m json.tool

api-containers:
    curl -s {{BACKEND_URL}}/docker/containers | python -m json.tool

api-images:
    curl -s {{BACKEND_URL}}/docker/images | python -m json.tool

api-volumes:
    curl -s {{BACKEND_URL}}/docker/volumes | python -m json.tool

open-frontend:
    open {{FRONTEND_URL}}

open-api-docs:
    open {{BACKEND_URL}}/docs

urls:
    @echo "Frontend : {{FRONTEND_URL}}"
    @echo "Backend  : {{BACKEND_URL}}"
    @echo "Swagger  : {{BACKEND_URL}}/docs"

config:
    docker compose config

validate:
    docker compose config --quiet

docker-info:
    docker info

docker-socket:
    ls -lah /var/run/docker.sock

tree:
    tree -I 'node_modules|dist|__pycache__|.venv|.git'
