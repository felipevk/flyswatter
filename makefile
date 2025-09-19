DB_SERVICE ?= db
API_SERVICE ?= api
TEST_DB ?= appdb_test

.PHONY: db-up db-down db-create-test db-drop-test test psql-dev psql-test migrate-dev migrate-base-dev revision

db-up:
	docker compose up -d db

db-down:
	docker compose stop db

db-create-test: db-up
	# create appdb_test if missing
	docker compose exec db psql -U app -d postgres -tc \
	"SELECT 1 FROM pg_database WHERE datname = '$(TEST_DB)';" | grep -q 1 \
	|| docker compose exec db psql -U app -d postgres -c "CREATE DATABASE $(TEST_DB);"

db-drop-test: db-up
	# drop appdb_test database if exists
	docker compose exec db psql -U app -d postgres -tc \
	"SELECT 1 FROM pg_database WHERE datname = '$(TEST_DB)';" | grep -q 1 \
	|| docker compose exec db psql -U app -d postgres -c "DROP DATABASE $(TEST_DB);"

test: db-up
	# load .env.test into the environment and run pytest from host
	ENV=.env.test bash -lc 'set -a; source $$ENV; set +a; poetry run pytest -q'

psql:
	docker compose exec db bash -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

psql-test:
	docker compose exec db bash -lc 'psql -U app -d $(TEST_DB)'

migrate-dev:
	poetry run alembic upgrade head

migrate-base-dev:
	poetry run alembic downgrade base

revision:
	# make revision msg="Updated user table"
	poetry run alembic revision --autogenerate -m "$(msg)"