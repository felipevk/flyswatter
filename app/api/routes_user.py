from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.session import engine, SessionLocal
from typing import Annotated
from .dto import UserCreate, UserEdit, UserRead
from sqlalchemy import select, insert, update
from app.db.models import User
from app.core.security import verify_password, get_password_hash, create_access_token, get_token_payload, Token

router = APIRouter(tags=["user"])

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

@router.post("/deleteuser/{username}")
async def delete_user(username: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    with SessionLocal() as session:
        userDB = get_user(username)
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
async def delete_user(editReq: UserEdit, current_user: Annotated[User, Depends(get_current_active_user)]):
    with SessionLocal() as session:
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
async def read_user(username: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    userDB = get_user(username)
    if not userDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return UserRead(
        email=userDB.email,username=userDB.username,full_name=userDB.name,admin=userDB.admin,disabled=userDB.disabled
        )
