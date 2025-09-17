from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.models import User
from app.db.session import engine, SessionLocal
from app.core.security import verify_password, get_token_payload, Token
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(username: str) -> User:
    with SessionLocal() as session:
        userQuery = select(User).where(User.username == username)
        userDB = session.execute(userQuery).scalars().first()
        if not userDB:
            return False
        return userDB

def authenticate_user(username: str, password: str):
    userDB = get_user(username)
    if not userDB:
            return False
    if not verify_password(password, userDB.pass_hash):
            return False
    return userDB

def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = get_token_payload(token)
    if not payload:
        raise credentials_exception
    username = payload.get("sub")
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_user_from_token)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user