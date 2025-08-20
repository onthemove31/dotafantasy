SHELL := /usr/bin/env bash

.PHONY: up down logs fmt lint test train

up:
	docker compose -f devops/docker-compose.yml up --build

down:
	docker compose -f devops/docker-compose.yml down -v

logs:
	docker compose -f devops/docker-compose.yml logs -f --tail=200

fmt:
	python -m black backend && ruff check --select I --fix backend || true

lint:
	ruff check backend && mypy backend || true

test:
	pytest -q backend

train:
	python backend/app/ml/train_player.py && python backend/app/ml/train_team.py
