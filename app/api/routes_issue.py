from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Integer, func, insert, select, update

from app.db.models import Issue, IssuePriority, IssueStatus, Project, User

from .dto import IssueCreate, IssueEditIn, IssueEditOut, IssueRead
from .routes_common import *

router = APIRouter(tags=["issue"])


@router.post("/issue/create", response_model=IssueRead)
async def create_issue(
    createReq: IssueCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> IssueRead:
    author = current_user.username
    projectQuery = select(Project).where(Project.public_id == createReq.project_id)
    projectDB = session.execute(projectQuery).scalars().first()

    assignedQuery = select(User).where(User.public_id == createReq.assignee_id)
    assignedUserDB = session.execute(assignedQuery).scalars().first()
    if not assignedUserDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.assigned_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )
    highestKeyQuery = select(func.max(Issue.key.cast(Integer))).where(
        Issue.project_id == projectDB.id
    )
    highestKey = session.execute(highestKeyQuery).first()[0]
    newKey = highestKey + 1 if highestKey is not None else 1
    newIssue = Issue(
        key=newKey,
        title=createReq.title,
        description=createReq.description,
        status=IssueStatus.OPEN,
        priority=createReq.priority,
        project=projectDB,
        author=current_user,
        assigned=assignedUserDB,
    )
    session.add(newIssue)
    session.commit()

    return IssueRead(
        id=newIssue.public_id,
        title=newIssue.title,
        key=f"{newIssue.project.key}-{newIssue.key}",
        description=newIssue.description,
        project_id=newIssue.project.public_id,
        assignee_id=newIssue.assigned.public_id,
        author_id=newIssue.author.public_id,
        priority=newIssue.priority,
        status=newIssue.status,
        created_at=newIssue.created_at.strftime("%a %d %b %Y, %I:%M%p"),
        updated_at=newIssue.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
    )


@router.get("/issue/mine", response_model=list[IssueRead])
async def read_user_issues(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[IssueRead]:
    pass


@router.post("/issue/edit/{issue_id}", response_model=IssueEditOut)
async def edit_issue(
    issue_id: str,
    editReq: IssueEditIn,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> IssueEditOut:
    newProjectQuery = select(Project).where(Project.public_id == editReq.project_id)
    newProjectDB = session.execute(newProjectQuery).scalars().first()
    if not newProjectDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project {editReq.project_id} not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    newAuthorQuery = select(User).where(User.public_id == editReq.author_id)
    newAuthorDb = session.execute(newAuthorQuery).scalars().first()
    if not newAuthorDb:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {editReq.author_id} not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    newAssignedQuery = select(User).where(User.public_id == editReq.assignee_id)
    newassignedDb = session.execute(newAssignedQuery).scalars().first()
    if not newassignedDb:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {editReq.assignee_id} not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    issueQuery = select(Issue).where(Issue.public_id == issue_id)
    issueDB = session.execute(issueQuery).scalars().first()
    if not issueDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.issue_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )
    issueDB.title = editReq.title
    issueDB.key = editReq.key
    issueDB.author = newAuthorDb
    issueDB.assigned = newassignedDb
    issueDB.description = editReq.description
    issueDB.status = editReq.status
    issueDB.priority = editReq.priority
    issueDB.project = newProjectDB

    session.commit()
    return IssueEditOut(
        id=issueDB.public_id,
        title=issueDB.title,
        key=f"{issueDB.project.key}-{issueDB.key}",
        description=issueDB.description,
        project_id=issueDB.project.public_id,
        assignee_id=issueDB.assigned.public_id,
        author_id=issueDB.author.public_id,
        priority=issueDB.priority,
        status=issueDB.status,
        created_at=issueDB.created_at.strftime("%a %d %b %Y, %I:%M%p"),
        updated_at=issueDB.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
    )


@router.post("/issue/resolve/{issue_id}", response_model=IssueRead)
async def resolve_issue(
    issue_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> IssueRead:
    pass


@router.post("/issue/delete/{issue_id}")
async def delete_issue(
    issue_id: str,
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    issueQuery = select(Issue).where(Issue.public_id == issue_id)
    issueDB = session.execute(issueQuery).scalars().first()
    if not issueDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.issue_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )

    session.delete(issueDB)
    session.commit()

    return {"status": apiMessages.issue_deleted}


@router.get("/issue/{issue_id}", response_model=IssueRead)
async def read_issue(
    issue_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> IssueRead:
    issueQuery = select(Issue).where(Issue.public_id == issue_id)
    issueDB = session.execute(issueQuery).scalars().first()
    if not issueDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.issue_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return IssueRead(
        id=issueDB.public_id,
        title=issueDB.title,
        key=f"{issueDB.project.key}-{issueDB.key}",
        description=issueDB.description,
        project_id=issueDB.project.public_id,
        assignee_id=issueDB.assigned.public_id,
        author_id=issueDB.author.public_id,
        priority=issueDB.priority,
        status=issueDB.status,
        created_at=issueDB.created_at.strftime("%a %d %b %Y, %I:%M%p"),
        updated_at=issueDB.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
    )
