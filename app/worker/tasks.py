from .celery_app import app
from time import sleep
from app.db.models import Job, JobResultKind, JobState
from app.db.session import SessionLocal
from datetime import datetime
from sqlalchemy import select
from fastapi import HTTPException, status
from app.api.routes_common import apiMessages

# bind is required for retries
# TODO add autoretry_for and set it to the errors that can occur here
# retry_backoff will exponentially delay between retries
@app.task(bind=True)
def generate_report(self, job_id: str, user_id: str, retry_backoff=True, max_retries=5):
    session = SessionLocal()
    jobQuery = select(Job).where(Job.public_id == job_id)
    jobDB = session.execute(jobQuery).scalars().first()
    if not jobDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.job_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )

    jobDB.state = JobState.RUNNING
    jobDB.attempts += 1
    jobDB.started_at = datetime.now()
    session.commit()
    sleep(30)
    jobDB.state = JobState.SUCCEEDED
    jobDB.finished_at = datetime.now()
    session.commit()