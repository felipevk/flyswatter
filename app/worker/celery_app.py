from celery import Celery

from app.core.config import settings

app = Celery(
    "celery_app", broker=settings.redis.build_url(), backend=settings.redis.build_url()
)
app.autodiscover_tasks(["app.worker"])
