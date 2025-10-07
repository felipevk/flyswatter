from typing import Annotated

from fastapi import APIRouter, Depends, Response
from prometheus_client import generate_latest
from sqlalchemy import func, select

from app.core.metrics import (
    clear_jobs_gauges,
    set_jobs_enqueued_gauge,
    set_jobs_failed_gauge,
    set_jobs_succeeded_gauge,
)
from app.db.models import Job, JobState

from .routes_common import *

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics(session: Annotated[Session, Depends(get_session)]):
    succeededQuery = (
        select(Job.job_type, func.count(Job.job_type))
        .where(Job.state == JobState.SUCCEEDED)
        .group_by(Job.job_type)
    )
    succeededDB = session.execute(succeededQuery).all()

    queuedQuery = (
        select(Job.job_type, func.count(Job.job_type))
        .where(Job.state == JobState.QUEUED)
        .group_by(Job.job_type)
    )
    queuedDB = session.execute(queuedQuery).all()

    failedQuery = (
        select(Job.job_type, func.count(Job.job_type))
        .where(Job.state == JobState.FAILED)
        .group_by(Job.job_type)
    )
    failedDB = session.execute(failedQuery).all()

    clear_jobs_gauges()

    for job in succeededDB:
        set_jobs_succeeded_gauge(job[0], job[1])

    for job in queuedDB:
        set_jobs_enqueued_gauge(job[0], job[1])

    for job in failedDB:
        set_jobs_failed_gauge(job[0], job[1])

    return Response(generate_latest(), media_type="text/plain")
