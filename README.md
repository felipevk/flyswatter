# [flyswatter](https://flyswatter-api.onrender.com/docs) [![Run tests and linting](https://github.com/felipevk/flyswatter/actions/workflows/commit.yml/badge.svg)](https://github.com/felipevk/flyswatter/actions/workflows/makefile.yml) [![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
:bug:Issue Tracker API made with FastAPI and PostgreSQL.

## Features
- Bug Tracking
- User Creation and Login using JWT tokens
- API with CRUD operations such as <sub>/user/create</sub> <sub>/user/{user_id}</sub> <sub>/user/all</sub> <sub>/issue/edit/{issue_id}</sub>.
- All endpoints can be accessed at <sub>/docs</sub> using Swagger UI
- Errors logged in Sentry, metrics can be observed by Prometheus from <sub>/metrics</sub>
- Extensive suite of tests using pytest

## Setup
Create .env file following [.env.example](.env.example)
```
pip install --no-cache-dir poetry
poetry config virtualenvs.create false | poetry install --no-interaction --no-ansi
docker compose up --build -d
poetry run dotenv run -- python -m app.db.create_database
make demo
```

## API Preview
![Swagger UI](images/flyswatter_swagger_ui.png)

## Tools
- Python
- Poetry
- FastAPI
- PostgreSQL 
- SQLAlchemy
- Alembic
- Docker + docker-compose
- pytest
- Sentry
- Prometheus
