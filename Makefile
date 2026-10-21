.RECIPEPREFIX = >
.PHONY: check up down build logs test e2e lock reset

check:
> docker compose config -q

build:
> docker compose build

up: check
> docker compose up -d --build

down:
> docker compose down

logs:
> docker compose logs -f app

test:
> .venv/bin/pytest -q

e2e:
> ./scripts/endpoint_test.sh

lock:
> docker compose run --rm --no-deps app pip freeze > requirements.lock

reset:
> docker compose down -v

tf-init:
> cd infra && terraform init -backend-config=backend.hcl