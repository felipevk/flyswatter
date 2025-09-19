from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from .dto import ProjectCreate, ProjectEdit, ProjectRead
from sqlalchemy import select, insert, update
from app.db.models import User, Project
from app.core.security import get_password_hash, create_access_token, get_token_payload, Token

from .routes_common import *

router = APIRouter(tags=["project"])

@router.post("/project/create", response_model = ProjectRead)
async def create_project(
    createReq: ProjectCreate, 
    current_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)]) -> ProjectRead:
    author = current_user.username
    if any(project.key == createReq.key for project in current_user.projects):
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=apiMessages.projectkey_exists,
        headers={"WWW-Authenticate": "Bearer"}
        )
    newProject = Project(key=createReq.key, title=createReq.title, author=current_user)
    session.add(newProject)
    session.commit()

    return ProjectRead(
        id=newProject.public_id,
        title=newProject.title,
        key=newProject.key,
        author=newProject.author.username,
        created_at=newProject.created_at.strftime('%a %d %b %Y, %I:%M%p')
        )

@router.post("/project/edit", response_model = ProjectRead)
async def edit_project(
    editReq: ProjectEdit, 
    current_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)]) -> ProjectRead:
    newAuthorDb = get_user(editReq.author, session)
    if not newAuthorDb:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"User {editReq.author} not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    projectQuery = select(Project).where(
        Project.public_id == editReq.id
        )
    projectDB = session.execute(projectQuery).scalars().first()
    if not projectDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=apiMessages.project_not_found,
        headers={"WWW-Authenticate": "Bearer"}
        )
    projectDB.title = editReq.title
    projectDB.key = editReq.key
    projectDB.author = newAuthorDb

    session.commit()
    return ProjectRead(
        id=projectDB.public_id,
        title=projectDB.title,
        key=projectDB.key,
        author=projectDB.author.username,
        created_at=projectDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
    )

@router.get("/project/mine", response_model = list[ProjectRead])
async def read_user_projects(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]) -> list[ProjectRead]:
    projectQuery = select(Project).where(
        Project.user_id == current_user.id
        )
    projectsDB = session.execute(projectQuery).scalars()
    myProjects = []
    for project in projectsDB:
        myProjects.append(
            ProjectRead(
                id=project.public_id,
                title=project.title,
                key=project.key,
                author=project.author.username,
                created_at=project.created_at.strftime('%a %d %b %Y, %I:%M%p'))
            )
    
    return myProjects

@router.get("/project/{project_id}", response_model = ProjectRead)
async def read_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]) -> ProjectRead:
    projectQuery = select(Project).where(
        Project.public_id == project_id
        )
    projectDB = session.execute(projectQuery).scalars().first()
    if not projectDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=apiMessages.project_not_found,
        headers={"WWW-Authenticate": "Bearer"}
        )
    
    return ProjectRead(
        id=projectDB.public_id,
        title=projectDB.title,
        key=projectDB.key,
        author=projectDB.author.username,
        created_at=projectDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
        )