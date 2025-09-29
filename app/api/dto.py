from pydantic import BaseModel

from app.db.models import IssuePriority, IssueStatus, Job, JobResultKind, JobState

from typing import Any, Mapping

class JobBasic(BaseModel):
    id: str
    user_id: str
    job_type: str
    status: JobState

class JobRead(JobBasic):
    attempts: int = 0

    started_at: str | None = None
    finished_at: str | None = None
    updated_at: str

    last_error: str | None = None
    error_kind: str | None = None
    error_payload: Mapping[str, Any]|None | None = None

    result_kind: JobResultKind | None = None
    artifact_id: int | None = None

    def __init__(self, jobDB : Job):
        self.id=jobDB.public_id,
        self.user_id=jobDB.user.public_id,
        self.job_type=jobDB.job_type,
        self.status=jobDB.state,
        self.attempts=jobDB.attempts,
        
        self.started_at=jobDB.started_at.strftime("%a %d %b %Y, %I:%M%p") if jobDB.started_at is not None else None,
        self.updated_at=jobDB.updated_at.strftime("%a %d %b %Y, %I:%M%p"),
        self.finished_at=jobDB.finished_at.strftime("%a %d %b %Y, %I:%M%p") if jobDB.finished_at is not None else None,

        self.last_error = jobDB.last_error,
        self.error_kind = jobDB.error_kind,
        self.error_payload = jobDB.error_payload,

        self.result_kind = jobDB.result_kind,
        self.artifact_id = jobDB.artifact_id,

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

class UserReport(JobBasic):
    pass

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


class IssueEditIn(IssueCreate):
    key: str
    status: IssueStatus
    author_id: str


class IssueEditOut(IssueEditIn):
    id: str
    created_at: str
    updated_at: str


class IssueRead(IssueEditOut):
    pass


class CommentCreate(BaseModel):
    issue_id: str
    body: str


class CommentEditIn(CommentCreate):
    pass


class CommentEditOut(CommentEditIn):
    id: str
    author_id: str
    created_at: str
    updated_at: str


class CommentRead(CommentEditOut):
    pass
