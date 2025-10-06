from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Token, get_token_payload, verify_password
from app.db.models import User
from app.db.session import create_session, engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Messages(BaseModel):
    token_auth_fail: str = "Could not validate credentials"
    inactive_user: str = "Inactive user"
    requires_admin: str = "User requires admin access"
    username_exists: str = "Username already exists"
    email_exists: str = "Email already registered"
    login_fail: str = "Incorrect username or password"
    refresh_not_found: str = "Refresh token not found"
    refresh_revoked: str = "Token already revoked"
    user_not_found: str = "User not found"
    user_deleted: str = "User deleted"
    projectkey_exists: str = "Project key already exists"
    project_not_found: str = "Project not found"
    project_deleted: str = "Project deleted"
    issuekey_exists: str = "Issue key already exists"
    issue_not_found: str = "Issue not found"
    issue_deleted: str = "Issue deleted"
    assigned_not_found: str = "Issue assigned user not found"
    comment_not_found: str = "Comment not found"
    comment_deleted: str = "Comment deleted"
    user_not_author: str = "Only the author can perform this operation"
    requires_idempotency_key: str = "Idempotency-Key header required"
    job_not_found: str = "Job not found"
    artifact_not_found: str = "Artifact not found"
    job_accepted: str = "Job accepted"


apiMessages = Messages()


# Will return session at first time it's driven by fastapi
# and it will call it again once the endpoint returns
# Additionally, any other functions that has this as a dependency will share the same cached session
def get_session() -> Session:
    session = create_session()
    try:
        yield session
    finally:
        session.close()


def get_user(username: str, session: Session) -> User:
    userQuery = select(User).where(User.username == username)
    userDB = session.execute(userQuery).scalars().first()
    if not userDB:
        return False
    return userDB


def get_user_from_id(id: str, session: Session) -> User:
    userQuery = select(User).where(User.public_id == id)
    userDB = session.execute(userQuery).scalars().first()
    if not userDB:
        return False
    return userDB


def authenticate_user(username: str, password: str, session: Session):
    userDB = get_user(username, session)
    if not userDB:
        return False
    if not verify_password(password, userDB.pass_hash):
        return False
    return userDB


def get_user_from_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=apiMessages.token_auth_fail,
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = get_token_payload(token)
    if not payload:
        raise credentials_exception
    username = payload.get("sub")
    user = get_user(username, session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_user_from_token)],
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=apiMessages.inactive_user
        )
    return current_user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=apiMessages.requires_admin
        )
    return current_user

async def require_idempotency_key(
    idem_key: str = Header(alias="Idempotency-Key")
)->str:
    if not idem_key:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=apiMessages.requires_admin
        )
    return idem_key
