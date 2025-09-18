from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    password: str

class UserEdit(UserCreate):
    id: str
    admin: bool = False
    disabled: bool = False

class UserRead(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None = None
    admin: bool = False
    disabled: bool = False
    created_at: str

class ProjectCreate(BaseModel):
    title: str
    key: str

class ProjectRead(ProjectCreate):
    id: str
    author: str
    created_at: str

class ProjectEdit(ProjectRead):
    pass