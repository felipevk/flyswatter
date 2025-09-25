from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import insert, select

from app.api.dto import IssueCreate, IssueEditIn, IssueEditOut, IssueRead
from app.api.routes_common import Token, apiMessages
from app.core.config import settings
from app.db.models import Issue, IssuePriority, IssueStatus, Project, User
from app.main import app

from .conftest import db_session
from .test_routes_common import *


def test_createissue_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toCreate = IssueCreate(
        project_id=projectDB.public_id,
        title="New Issue",
        description="An issue has been found",
        assignee_id=anotherUserDB.public_id,
        priority=IssuePriority.MEDIUM,
    )
    toExpect = IssueRead(
        id="",
        project_id=toCreate.project_id,
        title=toCreate.title,
        description=toCreate.description,
        assignee_id=toCreate.assignee_id,
        author_id=userDB.public_id,
        priority=toCreate.priority,
        status=IssueStatus.OPEN,
        key=f"{projectDB.key}-1",
        created_at="",
        updated_at="",
    )
    r = c.post(
        "/issue/create",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toCreate.model_dump(),
    )
    data = IssueRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id is not None
    assert data.project_id == toExpect.project_id
    assert data.title == toExpect.title
    assert data.description == toExpect.description
    assert data.author_id == toExpect.author_id
    assert data.assignee_id == toExpect.assignee_id
    assert data.priority == toExpect.priority
    assert data.status == toExpect.status
    assert data.key == toExpect.key
    assert data.created_at is not None
    assert data.description is not None


def test_createissue_assignednotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toCreate = IssueCreate(
        project_id=projectDB.public_id,
        title="New Issue",
        description="An issue has been found",
        assignee_id="Invalid",
        priority=IssuePriority.MEDIUM,
    )
    r = c.post(
        "/issue/create",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toCreate.model_dump(),
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.assigned_not_found


def test_readissue_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toExpect = IssueRead(
        id=issueDB.public_id,
        project_id=issueDB.project.public_id,
        title=issueDB.title,
        description=issueDB.description,
        assignee_id=issueDB.assigned.public_id,
        author_id=issueDB.author.public_id,
        priority=issueDB.priority,
        status=issueDB.status,
        key=f"{projectDB.key}-{issueDB.key}",
        created_at="",
        updated_at="",
    )
    r = c.get(
        f"/issue/{issueDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )
    data = IssueRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id is not None
    assert data.project_id == toExpect.project_id
    assert data.title == toExpect.title
    assert data.description == toExpect.description
    assert data.author_id == toExpect.author_id
    assert data.assignee_id == toExpect.assignee_id
    assert data.priority == toExpect.priority
    assert data.status == toExpect.status
    assert data.key == toExpect.key
    assert data.created_at is not None
    assert data.description is not None


def test_readissue_issuenotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toExpect = IssueRead(
        id=issueDB.public_id,
        project_id=issueDB.project.public_id,
        title=issueDB.title,
        description=issueDB.description,
        assignee_id=issueDB.assigned.public_id,
        author_id=issueDB.author.public_id,
        priority=issueDB.priority,
        status=issueDB.status,
        key=f"{projectDB.key}-{issueDB.key}",
        created_at="",
        updated_at="",
    )
    invalidId = "Invalid"
    r = c.get(
        f"/issue/{invalidId}", headers={"Authorization": f"Bearer {token.access_token}"}
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.issue_not_found


def xtest_readuserissues_success(db_session):
    c = TestClient(app)
    assert False


def xtest_readuserissues_issuenotfound(db_session):
    c = TestClient(app)
    assert False


def test_editissue_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = IssueEditIn(
        project_id=issueDB.project.public_id,
        title="Another Issue Title",
        description="The description has been updated",
        assignee_id=issueDB.assigned.public_id,
        author_id=issueDB.author.public_id,
        priority=IssuePriority.MEDIUM,
        key=issueDB.key,
        status=issueDB.status,
    )
    toExpect = IssueEditOut(
        id=issueDB.public_id,
        project_id=toEdit.project_id,
        title=toEdit.title,
        description=toEdit.description,
        assignee_id=toEdit.assignee_id,
        author_id=toEdit.author_id,
        priority=toEdit.priority,
        status=toEdit.status,
        key=f"{issueDB.project.key}-{toEdit.key}",
        created_at="",
        updated_at="",
    )
    r = c.post(
        f"/issue/edit/{issueDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump(),
    )
    data = IssueEditOut(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id == toExpect.id
    assert data.project_id == toExpect.project_id
    assert data.title == toExpect.title
    assert data.description == toExpect.description
    assert data.author_id == toExpect.author_id
    assert data.assignee_id == toExpect.assignee_id
    assert data.priority == toExpect.priority
    assert data.status == toExpect.status
    assert data.key == toExpect.key
    assert data.created_at is not None
    assert data.description is not None


def test_editissue_issuenotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = IssueEditIn(
        project_id=issueDB.project.public_id,
        title="Another Issue Title",
        description="The description has been updated",
        assignee_id=issueDB.assigned.public_id,
        author_id=issueDB.assigned.public_id,
        priority=IssuePriority.MEDIUM,
        key=issueDB.key,
        status=issueDB.status,
    )
    invalidId = "Invalid"
    r = c.post(
        f"/issue/edit/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump(),
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.issue_not_found


def test_editissue_authornotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = IssueEditIn(
        project_id=issueDB.project.public_id,
        title="Another Issue Title",
        description="The description has been updated",
        assignee_id=issueDB.assigned.public_id,
        author_id="Invalid",
        priority=IssuePriority.MEDIUM,
        key=issueDB.key,
        status=issueDB.status,
    )
    r = c.post(
        f"/issue/edit/{issueDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump(),
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == f"User {toEdit.author_id} not found"


def test_editissue_assignednotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = IssueEditIn(
        project_id=issueDB.project.public_id,
        title="Another Issue Title",
        description="The description has been updated",
        assignee_id="Invalid",
        author_id=issueDB.author.public_id,
        priority=IssuePriority.MEDIUM,
        key=issueDB.key,
        status=issueDB.status,
    )
    r = c.post(
        f"/issue/edit/{issueDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump(),
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == f"User {toEdit.assignee_id} not found"


def test_editissue_projectnotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = IssueEditIn(
        project_id="Invalid",
        title="Another Issue Title",
        description="The description has been updated",
        assignee_id=issueDB.assigned.public_id,
        author_id=issueDB.author.public_id,
        priority=IssuePriority.MEDIUM,
        key=issueDB.key,
        status=issueDB.status,
    )
    r = c.post(
        f"/issue/edit/{issueDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump(),
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == f"Project {toEdit.project_id} not found"


def xtest_resolveissue_success(db_session):
    c = TestClient(app)
    assert False


def test_deleteissue_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    r = c.post(
        f"/issue/delete/{issueDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == apiMessages.issue_deleted


def test_deleteissue_issuenotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    invalidId = "Invalid"
    r = c.post(
        f"/issue/delete/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.issue_not_found


def test_deleteissue_usernotadmin(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True,
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False,
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(id=None, title="Test Project", key="PROJ", author=userDB)
    db_session.add(projectDB)
    issueDB = Issue(
        id=None,
        title="New Issue",
        key="1",
        description="An issue has been found",
        status=IssueStatus.OPEN,
        priority=IssuePriority.MEDIUM,
        project=projectDB,
        author=userDB,
        assigned=anotherUserDB,
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    userDB.admin = False
    db_session.commit()
    r = c.post(
        f"/issue/delete/{issueDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json()["detail"] == apiMessages.requires_admin
