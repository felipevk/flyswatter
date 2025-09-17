from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from .config import settings
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth.accessTTL)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.auth.jwtSecret, algorithm=settings.auth.jwtAlg)
    return encoded_jwt

def get_token_payload(token):
    try:
        return jwt.decode(token, settings.auth.jwtSecret, algorithms=[settings.auth.jwtAlg])
    except InvalidTokenError:
        return False