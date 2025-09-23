import enum
from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class IssueStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssuePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MembershipRole(enum.Enum):
    OWNER = "owner"
    MAINTAINER = "maintainer"
    REPORTER = "reporter"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,  # API-facing ID
        nullable=False,
        index=True,
        default=lambda: uuid4().hex,
    )
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(60))
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    pass_hash: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationship property - does not get saved to DB
    # First parameter matches object type,
    # second matches the name of the relationship property in the other object model
    projects: Mapped[List["Project"]] = relationship(back_populates="author")

    # If the target table has multiple foreign keys for the same table,
    # you can set foreign_keys to specify which one to populate
    created_issues: Mapped[List["Issue"]] = relationship(
        back_populates="author", foreign_keys="Issue.author_id"
    )
    assigned_issues: Mapped[List["Issue"]] = relationship(
        back_populates="assigned", foreign_keys="Issue.assign_id"
    )

    comments: Mapped[List["Comment"]] = relationship(back_populates="author")

    memberships: Mapped[List["Membership"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "projects"
    # Makes it so the combination user + key is unique
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_post_user_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True, default=lambda: uuid4().hex
    )
    #TODO make key and title not unique
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    key: Mapped[str] = mapped_column(String(4), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # FK managed by sqlAlchemy, doesn't need to be set by our code
    # argument matches target table.field
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="projects")
    issues: Mapped[List["Issue"]] = relationship(back_populates="project")

    memberships: Mapped[List["Membership"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Membership(Base):
    __tablename__ = "memberships"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole, name="membership_role_enum")
    )

    project: Mapped["Project"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True, default=lambda: uuid4().hex
    )
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    # human key like APP-42
    key: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus, name="issue_status_enum")
    )
    priority: Mapped[IssuePriority] = mapped_column(
        Enum(IssuePriority, name="issue_priority_enum")
    )

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assign_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    project: Mapped["Project"] = relationship(back_populates="issues")
    author: Mapped["User"] = relationship(
        back_populates="created_issues", foreign_keys=[author_id]
    )
    assigned: Mapped["User"] = relationship(
        back_populates="assigned_issues", foreign_keys=[assign_id]
    )
    comments: Mapped[List["Comment"]] = relationship(back_populates="issue")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True, default=lambda: uuid4().hex
    )
    body: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"))

    author: Mapped["User"] = relationship(back_populates="comments")
    issue: Mapped["Issue"] = relationship(back_populates="comments")


class RefreshToken(Base):
    __tablename__ = "refresh"
    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
