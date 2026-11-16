COMPOSE := docker compose -f deploy/compose.yml --env-file deploy/.env

.PHONY: help up down ps logs psql migrate seed test lint fmt

help: ## Hedefleri listeler
	@grep -hE '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

up: ## Imaji build edip yigini ayaga kaldirir
	$(COMPOSE) up -d --build

down: ## Container'lari durdurur (volume'lara dokunmaz)
	$(COMPOSE) down

ps: ## Servis durumlari
	$(COMPOSE) ps

logs: ## app loglari
	$(COMPOSE) logs -f --tail=50 app

psql: ## postgres oturumu
	$(COMPOSE) exec postgres sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

migrate: ## Alembic migration'larini uygular
	$(COMPOSE) run --rm app alembic upgrade head

seed: ## 1000 deterministik kod + 1 sicak kod ekler
	$(COMPOSE) run --rm app python -m edge_lab.seed

test: ## Testler (yerelde, SQLite ile)
	cd app && uv run pytest -q

lint: ## ruff check + format kontrolu
	cd app && uv run ruff check . && uv run ruff format --check .

fmt: ## ruff format
	cd app && uv run ruff format .
