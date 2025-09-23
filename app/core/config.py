import os

from pydantic import BaseModel
from typing import Optional


def build_db_url() -> str:
    user = os.getenv("POSTGRES_USER", "")
    pwd = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("DB_HOST", "")
    port = int(os.getenv("DB_PORT", ""))
    db = os.getenv("POSTGRES_DB", "")
    driver = os.getenv("DB_DRIVER", "")
    return f"{driver}://{user}:{pwd}@{host}:{port}/{db}"


class AuthSettings(BaseModel):
    jwtAlg: str = os.getenv("JWT_ALG", "")
    jwtSecret: str = os.getenv("JWT_SECRET", "")
    accessTTL: int = int(os.getenv("ACCESS_TTL_MIN", ""))
    refreshTTL: int = int(os.getenv("REFRESH_TTL_DAYS", ""))

class SentrySettings(BaseModel):
    sentry_dsn: Optional[str] =  os.getenv("SENTRY_DSN", None)
    sample_rate: Optional[str] =  os.getenv("SENTRY_SAMPLE_RATE", 1.0)


class Settings(BaseModel):
    database_url: str = build_db_url()
    auth: AuthSettings = AuthSettings()
    env: str = os.getenv("APP_ENV", "")
    sentry: SentrySettings = SentrySettings()


settings = Settings()
