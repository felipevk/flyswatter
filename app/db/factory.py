from .models import User, Project, Issue, IssueStatus, IssuePriority, Comment
from app.core.security import get_password_hash

def create_user(**overrides)-> User:
    defaults = { 
        "name": "John Doe",
        "username": "jdoe",
        "password": "secret",
        "email": "jdoe@jdoe.com",
        "admin": False,
        "disabled": False
    }
    defaults.update(overrides)
    defaults["pass_hash"] = get_password_hash(defaults["password"])
    defaults.pop("password", None)

    return User(**defaults)

def create_project(user: User, **overrides)-> Project:
    defaults = {
        "title": "Test Project",
        "key": "PROJ",
        "author": user
    }
    defaults.update(overrides)

    return Project(**defaults)

def create_issue(project: Project, owner: User, assigned: User, **overrides)-> Issue:
    defaults = {
        "title": "New Issue",
        "key": "1",
        "description": "An issue has been found",
        "status": IssueStatus.OPEN,
        "priority": IssuePriority.MEDIUM,
        "project": project,
        "author": owner,
        "assigned": assigned
    }
    defaults.update(overrides)

    return Issue(**defaults)

def create_comment(issue: Issue, author: User, **overrides)-> Comment:
    defaults = {
        "issue": issue,
        "body": "New Comment on current issue",
        "author": author
    }
    defaults.update(overrides)

    return Comment(**defaults)