from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from .dto import UserCreate, UserEdit, UserRead
from sqlalchemy import select, insert
from app.db.models import User
from app.core.security import get_password_hash, create_access_token, get_token_payload, Token

from .routes_common import *

router = APIRouter(tags=["user"])

@router.post("/createuser")
def create_user(createReq : UserCreate, session: Annotated[Session, Depends(get_session)]):
    usernameQuery = select(User).where(User.username == createReq.username)
    emailQuery = select(User).where(User.email == createReq.email)
    if session.execute(usernameQuery).all():
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Username already exists",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if session.execute(emailQuery).all():
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already registered",
        headers={"WWW-Authenticate": "Bearer"},
    )
    newUser = User(
        id=None, 
        username=createReq.username, 
        email=createReq.email, 
        name=createReq.full_name, 
        pass_hash=get_password_hash(createReq.password)
        )
    session.add(newUser)
    session.commit()
    return {"status": "User Created with Success"}

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]) -> Token:
    userDB = authenticate_user(form_data.username, form_data.password, session)
    if not userDB:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": userDB.username}
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/deleteuser/{username}")
async def delete_user(
    username: str, 
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]):
    userDB = get_user(username, session)
    if not userDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Username not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
        session.delete(userDB)
        session.commit()
    return {"status": "User Deleted"}

@router.post("/edituser")
async def delete_user(
    editReq: UserEdit, 
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]):
    userQuery = select(User).where(User.username == editReq.username)
    userDB = session.execute(userQuery).scalars().first()
    if not userDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Username not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    userDB.email = editReq.email
    userDB.name = editReq.full_name
    userDB.pass_hash = get_password_hash(editReq.password)
    userDB.disabled = editReq.disabled
    userDB.admin = editReq.admin
    session.commit()
    return {"status": "User edited with success"}

@router.get("/user/{username}")
async def read_user(
    username: str, 
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]):
    userDB = get_user(username, session)
    if not userDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return UserRead(
        email=userDB.email,username=userDB.username,full_name=userDB.name,admin=userDB.admin,disabled=userDB.disabled
        )
