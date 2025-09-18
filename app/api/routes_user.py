from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from .dto import UserCreate, UserEdit, UserRead
from sqlalchemy import select, insert
from app.db.models import User, RefreshToken
from app.core.security import get_password_hash, create_access_token, create_refresh_token, get_token_expiry, Token
from uuid import uuid4
from datetime import datetime, timezone

from .routes_common import *

router = APIRouter(tags=["user"])

def generate_new_token(userDB: User, session: Session) -> Token:
    access_token = create_access_token(
        data={"sub": userDB.username}
    )

    refresh_jti =  uuid4().hex
    refresh_token = create_refresh_token(
        data={"sub": userDB.username},
        jti=refresh_jti
    )

    # Refresh tokens live on the DB
    tokenDB = RefreshToken(
        public_id=refresh_jti, 
        expires_at=datetime.fromtimestamp(get_token_expiry(refresh_token)), 
        user=userDB,
        )
    session.add(tokenDB)
    session.commit()

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/user/create")
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

@router.post("/token", response_model = Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]) -> Token:
    userDB = authenticate_user(form_data.username, form_data.password, session)
    if not userDB:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Incorrect username or password")
    
    return generate_new_token(userDB, session)

@router.post("/refresh", response_model = Token)
async def refresh(
    token: str,
    session: Annotated[Session, Depends(get_session)]) -> Token:
    payload = get_token_payload(token)
    if not payload:
        raise credentials_exception
    username = payload.get("sub")
    jti = payload.get("jti")
    userDB = get_user(username, session)
    if not userDB:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Incorrect username or password")
    
    refreshQuery = select(RefreshToken).where(RefreshToken.public_id == jti)
    refreshDB = session.execute(refreshQuery).scalars().first()
    if not refreshDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Refresh token not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
    refreshDB.revoked_at = datetime.now(timezone.utc)
    session.commit()

    return generate_new_token(userDB, session)

@router.post("/user/delete/{user_id}")
async def delete_user(
    user_id: str, 
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]):
    userDB = get_user_from_id(user_id, session)
    if not userDB:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Username not found",
        headers={"WWW-Authenticate": "Bearer"}
        )
        session.delete(userDB)
        session.commit()
    return {"status": "User Deleted"}

@router.post("/user/edit")
async def edit_user(
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
    
@router.get("/user/all", response_model = list[UserRead])
async def read_all_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]) -> UserRead:
    
    userQuery = select(User)
    userDB = session.execute(userQuery).scalars()

    result = []
    for user in userDB:
        result.append(UserRead(
            id=user.public_id, 
            email=user.email,
            username=user.username,
            full_name=user.name,
            admin=user.admin,
            disabled=user.disabled,
            created_at=user.created_at.strftime('%a %d %b %Y, %I:%M%p')
        ))

    return result

@router.get("/user/{user_id}", response_model = UserRead)
async def read_user(
    user_id: str, 
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)]) -> UserRead:
    userDB = get_user_from_id(user_id, session)
    if not userDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return UserRead(
            id=userDB.public_id, 
            email=userDB.email,
            username=userDB.username,
            full_name=userDB.name,
            admin=userDB.admin,
            disabled=userDB.disabled,
            created_at=userDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
        )
