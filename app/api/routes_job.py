from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.db.models import Job, JobResultKind, JobState

from .dto import JobRead, jobReadFrom
from .routes_common import *

router = APIRouter(tags=["job"])

@router.get("/jobs/all", response_model=list[JobRead])
async def read_all_jobs(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[JobRead]:
    jobQuery = select(Job)
    jobsDB = session.execute(jobQuery).scalars()
    allJobs = []
    for job in jobsDB:
        allJobs.append(jobReadFrom(job))

    return allJobs

@router.get("/jobs/failed", response_model=list[JobRead])
async def read_failed_jobs(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[JobRead]:
    jobQuery = select(Job).where(Job.state == JobState.FAILED)
    jobsDB = session.execute(jobQuery).scalars()
    allJobs = []
    for job in jobsDB:
        allJobs.append(jobReadFrom(job))

    return allJobs

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
    return jobReadFrom(jobDB)