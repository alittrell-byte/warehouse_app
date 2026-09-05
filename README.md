## Running test migrations
- run this when a model is changed or added - `docker compose run --rm migrator alembic revision --autogenerate -m "description"`

- then do a regular `docker compose up`