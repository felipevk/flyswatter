from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.session import engine, SessionLocal
from typing import Annotated
from .dto import UserCreate
from sqlalchemy import select, insert
from app.db.models import User
from app.core.security import verify_password, get_password_hash, create_access_token, Token

router = APIRouter(tags=["user"])

def authenticate_user(username: str, password: str):
    with SessionLocal() as session:
        userQuery = select(User).where(User.username == username)
        userDB = session.execute(userQuery).scalars().first()
        if not userDB:
            return False
        if not verify_password(password, userDB.pass_hash):
            return False
        return userDB

@router.post("/createuser")
def create_user(createReq : UserCreate):
    with SessionLocal() as session:
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
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    userDB = authenticate_user(form_data.username, form_data.password)
    if not userDB:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": userDB.username}
    )
    return Token(access_token=access_token, token_type="bearer")
