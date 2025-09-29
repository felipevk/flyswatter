from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.db.models import Job, JobResultKind, JobState

from .dto import JobRead
from .routes_common import *

router = APIRouter(tags=["job"])

@router.post("/jobs/all", response_model=list[JobRead])
async def read_all_jobs(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[JobRead]:
    pass

@router.post("/jobs/failed", response_model=list[JobRead])
async def read_failed_jobs(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[JobRead]:
    pass

@router.get("/jobs/{job_id}", response_model=JobRead)
async def read_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> JobRead:
    jobQuery = select(Job).where(Job.public_id == job_id)
    jobDB = session.execute(jobQuery).scalars().first()
    if not jobDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.job_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JobRead(jobDB)
    '''return JobRead(
        id=jobDB.public_id,
        user_id=jobDB.user.public_id,
        job_type=jobDB.job_type,
        status=jobDB.state,
        attempts=jobDB.attempts,
        
        started_at=jobDB.started_at.strftime("%a %d %b %Y, %I:%M%p") if jobDB.started_at is not None else None,
        updated_at=jobDB.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
        finished_at=jobDB.finished_at.strftime("%a %d %b %Y, %I:%M%p") if jobDB.finished_at is not None else None,

        last_error = jobDB.last_error,
        error_kind = jobDB.error_kind,
        error_payload = jobDB.error_payload,

        result_kind = jobDB.result_kind,
        artifact_id = jobDB.artifact_id,
    )'''