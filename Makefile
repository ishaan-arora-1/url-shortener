.PHONY: up down logs migrate test lint

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

migrate:
	docker compose exec api alembic upgrade head

test:
	pytest -q

lint:
	ruff check app tests
