import os
from typing import Optional

from pydantic import BaseModel


class AuthSettings(BaseModel):
    jwtAlg: str = os.getenv("JWT_ALG", "")
    jwtSecret: str = os.getenv("JWT_SECRET", "")
    accessTTL: int = int(os.getenv("ACCESS_TTL_MIN", ""))
    refreshTTL: int = int(os.getenv("REFRESH_TTL_DAYS", ""))


class SentrySettings(BaseModel):
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN", None)
    sample_rate: Optional[str] = os.getenv("SENTRY_SAMPLE_RATE", 1.0)

class DatabaseSettings(BaseModel):
    user: str = os.getenv("POSTGRES_USER", "")
    pwd: str = os.getenv("POSTGRES_PASSWORD", "")
    host: str = os.getenv("DB_HOST", "")
    port: int = int(os.getenv("DB_PORT", ""))
    db: str = os.getenv("POSTGRES_DB", "")
    driver: str = os.getenv("DB_DRIVER", "")

    def build_url(self) -> str:
        return f"{self.driver}://{self.user}:{self.pwd}@{self.host}:{self.port}/{self.db}"

class RedisSettings(BaseModel):
    host: Optional[str] = os.getenv("REDIS_HOST", "localhost")
    port: Optional[int] = os.getenv("REDIS_PORT", 6379)
    db: Optional[int] = os.getenv("REDIS_DB", 0)

    def build_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"

class Settings(BaseModel):
    env: str = os.getenv("APP_ENV", "")
    
    auth: AuthSettings = AuthSettings()
    database: DatabaseSettings = DatabaseSettings()
    sentry: SentrySettings = SentrySettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
