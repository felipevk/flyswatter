from fastapi import APIRouter

from app.core.config import settings

import sentry_sdk

router = APIRouter(tags=["sentry"])

if settings.sentry_dsn:
    sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=1.0,
            environment=settings.env,
        )

@router.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0