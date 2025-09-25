import sentry_sdk
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["sentry"])

if settings.sentry.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry.sentry_dsn,
        traces_sample_rate=settings.sentry.sample_rate,
        environment=settings.env,
    )


@router.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
