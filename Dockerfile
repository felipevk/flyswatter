# 1. Base image: lightweight Python
FROM python:3.12-slim

# 2. Set working directory inside the container
WORKDIR /flyswatter

# 3. Install Poetry (package manager)
RUN pip install --no-cache-dir poetry

# 4. Copy dependency files first (better build caching)
COPY pyproject.toml poetry.lock* ./

# 5. Install dependencies inside container
# Tells poetry to not create a venv since the container is already isolated
# Then it installs your dependencies as declared in pyproject.toml and poetry.lock.
# --no-ansi means no colored output to make logs cleaner in Docker
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# 6. Copy source code (host ./app → container /flyswatter/app)
COPY app ./app

# 7. Define the default startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 8. Forcing the environment to change
# In future projects, use .env.docker
ENV APP_ENV=docker