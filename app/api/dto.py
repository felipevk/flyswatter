from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    password: str

class UserEdit(UserCreate):
    admin: bool
    disabled:bool