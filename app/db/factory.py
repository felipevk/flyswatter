import hashlib
import json
from uuid import uuid4

from app.core.security import get_password_hash

from .models import (
    Artifact,
    Comment,
    Issue,
    IssuePriority,
    IssueStatus,
    Job,
    JobState,
    Project,
    User,
)


# ** passed as a parameter allows the caller to provide any extra number of keyword arguments not captured by any other parameters,
# which are then stored as a dictionary.
def create_user(**overrides) -> User:
    defaults = {
        "name": "John Doe",
        "username": "jdoe",
        "password": "secret",
        "email": "jdoe@jdoe.com",
        "admin": False,
        "disabled": False,
    }
    defaults.update(overrides)
    defaults["pass_hash"] = get_password_hash(defaults["password"])
    defaults.pop("password", None)

    return User(**defaults)


def create_project(user: User, **overrides) -> Project:
    defaults = {"title": "Test Project", "key": "PROJ", "author": user}
    defaults.update(overrides)

    return Project(**defaults)


def create_issue(project: Project, owner: User, assigned: User, **overrides) -> Issue:
    defaults = {
        "title": "New Issue",
        "key": "1",
        "description": "An issue has been found",
        "status": IssueStatus.OPEN,
        "priority": IssuePriority.MEDIUM,
        "project": project,
        "author": owner,
        "assigned": assigned,
    }
    defaults.update(overrides)

    return Issue(**defaults)


def create_comment(issue: Issue, author: User, **overrides) -> Comment:
    defaults = {
        "issue": issue,
        "body": "New Comment on current issue",
        "author": author,
    }
    defaults.update(overrides)

    return Comment(**defaults)


def create_request_hash(body: dict | None, query: dict | None) -> str:
    if body:
        payload = body
    elif query:
        payload = query
    else:
        payload = {"__empty__": True}

    # Keep keys sorted and clean up spaces so the order of keys or spaces don't affect hash
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def create_job(user: User, **overrides) -> Job:
    defaults = {
        "user": user,
        "job_type": "generate-report",
        "state": JobState.QUEUED,
        "idempotency_key": uuid4().hex,
        "request_hash": create_request_hash(None, None),
    }
    defaults.update(overrides)

    return Job(**defaults)


def create_artifact(job: Job, **overrides) -> Artifact:
    defaults = {"url": "", "job": job}
    defaults.update(overrides)

    return Artifact(**defaults)
