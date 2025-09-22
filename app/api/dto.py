from pydantic import BaseModel
from app.db.models import IssueStatus, IssuePriority

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


class IssueCreate(BaseModel):
    project_id: str
    title: str
    description: str
    assignee_id: str
    priority: IssuePriority


class IssueEdit(IssueCreate):
    status: IssueStatus


class IssueRead(IssueEdit):
    created_at: str
    updated_at: str

class CommentCreate(BaseModel):
    issue_id: str
    body: str

class CommentEdit(CommentCreate):
    pass

class CommentRead(CommentCreate):
    author: str
    created_at: str
    updated_at: str
