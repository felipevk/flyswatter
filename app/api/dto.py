from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    password: str

class UserEdit(UserCreate):
    admin: bool = False
    disabled: bool = False

class UserRead(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    admin: bool = False
    disabled: bool = False

class ProjectCreate(BaseModel):
    title: str
    key: str

class ProjectRead(ProjectCreate):
    author: str

class ProjectEdit(ProjectRead):
    pass