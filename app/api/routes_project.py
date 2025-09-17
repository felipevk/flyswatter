from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from .dto import ProjectCreate, ProjectEdit, ProjectRead
from sqlalchemy import select, insert, update
from app.db.models import User, Project
from app.core.security import get_password_hash, create_access_token, get_token_payload, Token

from .routes_common import *

router = APIRouter(tags=["project"])

@router.post("/project/create")
async def create_project(
    createReq: ProjectCreate, 
    current_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)]):
    author = current_user.username
    if any(project.key == createReq.key for project in current_user.projects):
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Project with key already exists",
        headers={"WWW-Authenticate": "Bearer"}
        )
    newProject = Project(key=createReq.key, title=createReq.title, author=current_user)
    session.add(newProject)
    session.commit()
    return {"status": "Project created with success"}

@router.get("/project/read")
async def read_project(
    author: str, 
    key: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]) -> ProjectRead:
    authorDb = get_user(author, session)
    if not authorDb:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    projectQuery = select(Project).where(
        Project.key == key and Project.user_id == authorDb.id
        )
    projectDB = session.execute(projectQuery).scalars().first()
    if not projectDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Project not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    
    return ProjectRead(title=projectDB.title,key=projectDB.key,author=authorDb.username)

@router.post("/project/edit")
async def edit_project(
    author: str, 
    key: str,
    editReq: ProjectEdit, 
    current_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)]):
    currAuthorDb = get_user(author, session)
    newAuthorDb = get_user(editReq.author, session)
    if not currAuthorDb:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"User {author} not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    if not newAuthorDb:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"User {editReq.author} not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    projectQuery = select(Project).where(
        Project.key == key and Project.user_id == currAuthorDb.id
        )
    projectDB = session.execute(projectQuery).scalars().first()
    if not projectDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Project not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    projectDB.title = editReq.title
    projectDB.key = editReq.key
    projectDB.author = newAuthorDb

    session.commit()
    return {"status": "Project edited with success"}

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
            ProjectRead(title=project.title,key=project.key,author=current_user.username)
            )
    
    return myProjects