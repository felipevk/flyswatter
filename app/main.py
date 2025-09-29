from uuid import uuid4

import sentry_sdk
from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.metrics import inc_request_count

from .api.routes_comment import router as comment_router
from .api.routes_health import router as health_router
from .api.routes_issue import router as issue_router
from .api.routes_project import router as project_router
from .api.routes_sentry import router as sentry_router
from .api.routes_user import router as user_router
from .api.routes_job import router as job_router

app = FastAPI(title="Flyswatter API")
app.include_router(health_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(issue_router)
app.include_router(comment_router)
app.include_router(sentry_router)
app.include_router(job_router)
app.mount("/metrics", make_asgi_app())


@app.get("/")
def root():
    return {"ok": True}


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    if settings.sentry.sentry_dsn:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("request_id", request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    inc_request_count(request, response)
    return response
