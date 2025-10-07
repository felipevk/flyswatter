from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes_common import apiMessages
from app.artifacts.pdf_generator import monthly_report_pdf
from app.blob.storage import upload
from app.core.errors import AppError, BlobError, ConnectionError, ExternalServiceError
from app.core.monitoring import sentry_init
from app.db.factory import create_artifact
from app.db.models import Job, JobResultKind, JobState
from app.db.monthly_report import generate_monthly_report
from app.db.session import create_session

from .celery_app import app

sentry_init()


def fetch_task(session: Session, job_id: str) -> Job:
    jobQuery = select(Job).where(Job.public_id == job_id)
    jobDB = session.execute(jobQuery).scalars().first()
    if not jobDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.job_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return jobDB


def start_task(session: Session, job: Job):
    job.state = JobState.RUNNING
    job.attempts += 1
    job.started_at = datetime.now()
    session.commit()


def error_task(session: Session, job: Job, e: AppError):
    job.state = JobState.FAILED
    job.last_error = str(e)
    job.error_kind = type(e).__name__
    session.commit()


def succeed_task_artifact(session: Session, job: Job, artifactUrl: str):
    job.state = JobState.SUCCEEDED
    job.result_kind = JobResultKind.ARTIFACT
    newArtifact = create_artifact(job, url=artifactUrl)
    session.add(newArtifact)
    session.commit()


def finish_task(session: Session, job: Job):
    job.finished_at = datetime.now()
    session.commit()


# bind is required for retries
# TODO add autoretry_for and set it to the errors that can occur here
# retry_backoff will exponentially delay between retries
@app.task(
    bind=True,
    retry_backoff=True,
    max_retries=5,
    autoretry_for=(BlobError, ConnectionError, ExternalServiceError),
)
def generate_report(self, job_id: str, user_id: str):
    session = create_session()
    jobDB = fetch_task(session, job_id)
    start_task(session, jobDB)

    try:
        report = generate_monthly_report(session, user_id)
        if report is None:
            raise AppError(f"Monthly report not found for user {user_id}")
        monthly_report_pdf(report, "output.pdf")
        report_url = upload("output.pdf", "reports")

        succeed_task_artifact(session, jobDB, report_url)

    except (ConnectionError, ExternalServiceError) as e:
        error_task(session, jobDB, e)
        raise e

    except AppError as e:
        error_task(session, jobDB, e)
        finish_task(session, jobDB)
        raise e
