from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.db.models import Artifact

from .dto import ArtifactRead, artifactReadFrom
from .routes_common import *

router = APIRouter(tags=["artifact"])

@router.get("/artifacts/all", response_model=list[ArtifactRead])
async def read_all_artifacts(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[ArtifactRead]:
    artifactQuery = select(Artifact)
    artifactsDB = session.execute(artifactQuery).scalars()
    allArtifacts = []
    for artifact in artifactsDB:
        allArtifacts.append(artifactReadFrom(artifact))

    return allArtifacts


@router.get("/artifacts/{artifact_id}", response_model=ArtifactRead)
async def read_artifact(
    artifact_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> ArtifactRead:
    artifactQuery = select(Artifact).where(Artifact.public_id == artifact_id)
    artifactDB = session.execute(artifactQuery).scalars().first()
    if not artifactDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.artifact_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return artifactReadFrom(artifactDB)