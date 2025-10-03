import sentry_sdk
from app.core.config import settings

def sentry_init():
    if settings.sentry.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry.sentry_dsn,
            traces_sample_rate=settings.sentry.sample_rate,
            environment=settings.env,
        )