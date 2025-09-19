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
    refresh_token: str
    token_type: str

def create_access_token(data: dict, jti: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth.accessTTL)
    to_encode.update({"exp": expire})
    to_encode.update({"jti": jti})
    to_encode.update({"iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.auth.jwtSecret, algorithm=settings.auth.jwtAlg)
    return encoded_jwt

def create_refresh_token(data: dict, jti: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.auth.refreshTTL)
    to_encode.update({"exp": expire})
    to_encode.update({"jti": jti})
    to_encode.update({"iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.auth.jwtSecret, algorithm=settings.auth.jwtAlg)
    return encoded_jwt

def get_token_payload(token):
    try:
        return jwt.decode(token, settings.auth.jwtSecret, algorithms=[settings.auth.jwtAlg])
    except InvalidTokenError:
        # Also hits this path if token is expired
        return False

def get_token_expiry(token):
    try:
        decoded = jwt.decode(token, settings.auth.jwtSecret, algorithms=[settings.auth.jwtAlg])
        return decoded.get("exp")
    except InvalidTokenError:
        return False