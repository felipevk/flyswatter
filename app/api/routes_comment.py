from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select, update

from app.db.models import Comment, Issue, User

from .dto import CommentCreate, CommentEditIn, CommentEditOut, CommentRead
from .routes_common import *

router = APIRouter(tags=["comment"])


@router.post("/comment/create", response_model=CommentRead)
async def create_comment(
    createReq: CommentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> CommentRead:
    issueQuery = select(Issue).where(Issue.public_id == createReq.issue_id)
    issueDB = session.execute(issueQuery).scalars().first()
    if not issueDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.issue_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )

    newComment = Comment(body=createReq.body, author=current_user, issue=issueDB)
    session.add(newComment)
    session.commit()

    return CommentRead(
        id=newComment.public_id,
        issue_id=newComment.issue.public_id,
        body=newComment.body,
        author_id=newComment.author.public_id,
        created_at=newComment.created_at.strftime("%a %d %b %Y, %I:%M%p"),
        updated_at=newComment.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
    )


# TODO
"""@router.get("/comment/mine", response_model=list[CommentRead])
async def read_user_comments(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[CommentRead]:
    pass


@router.get("/comment/issue/{issue_id}", response_model=list[CommentRead])
async def read_issue_comments(
    issue_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[CommentRead]:
    pass"""


@router.post("/comment/edit/{comment_id}", response_model=CommentEditOut)
async def edit_comment(
    comment_id: str,
    editReq: CommentEditIn,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> CommentEditOut:
    commentQuery = select(Comment).where(Comment.public_id == comment_id)
    commentDB = session.execute(commentQuery).scalars().first()
    if not commentDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.comment_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )
    isAdminOrAuthor = (
        current_user.admin or commentDB.author.public_id == current_user.public_id
    )
    if not isAdminOrAuthor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=apiMessages.user_not_author,
            headers={"WWW-Authenticate": "Bearer"},
        )
    newIssueQuery = select(Issue).where(Issue.public_id == editReq.issue_id)
    newIssueDB = session.execute(newIssueQuery).scalars().first()
    if not newIssueDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.issue_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )

    commentDB.body = editReq.body
    commentDB.issue = newIssueDB
    session.commit()

    return CommentEditOut(
        id=commentDB.public_id,
        issue_id=commentDB.issue.public_id,
        body=commentDB.body,
        author_id=commentDB.author.public_id,
        created_at=commentDB.created_at.strftime("%a %d %b %Y, %I:%M%p"),
        updated_at=commentDB.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
    )


@router.post("/comment/delete/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    commentQuery = select(Comment).where(Comment.public_id == comment_id)
    commentDB = session.execute(commentQuery).scalars().first()
    if not commentDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.comment_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )
    isAdminOrAuthor = (
        current_user.admin or commentDB.author.public_id == current_user.public_id
    )
    if not isAdminOrAuthor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=apiMessages.user_not_author,
            headers={"WWW-Authenticate": "Bearer"},
        )

    session.delete(commentDB)

    return {"status": apiMessages.comment_deleted}


@router.get("/comment/{comment_id}", response_model=CommentRead)
async def read_comment(
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
) -> CommentRead:
    commentQuery = select(Comment).where(Comment.public_id == comment_id)
    commentDB = session.execute(commentQuery).scalars().first()
    if not commentDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=apiMessages.comment_not_found,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CommentRead(
        id=commentDB.public_id,
        issue_id=commentDB.issue.public_id,
        body=commentDB.body,
        author_id=commentDB.author.public_id,
        created_at=commentDB.created_at.strftime("%a %d %b %Y, %I:%M%p"),
        updated_at=commentDB.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
    )
