from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import insert, select

from app.api.dto import CommentCreate, CommentEditIn, CommentEditOut, CommentRead
from app.api.routes_common import Token, apiMessages
from app.core.config import settings
from app.db.models import Comment, Issue, IssueStatus, IssuePriority, Project, User
from app.main import app

from .conftest import db_session

from .test_routes_common import *

def test_createcomment_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toCreate = CommentCreate(
        issue_id = issueDB.public_id,
        body = "Comment 1"
    )
    toExpect = CommentRead(
        id="",
        issue_id=toCreate.issue_id,
        body=toCreate.body,
        author_id=userDB.public_id,
        created_at="",
        updated_at=""
    )
    r = c.post(
        "/comment/create",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toCreate.model_dump()
    )
    data = CommentRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id is not None
    assert data.issue_id == toExpect.issue_id
    assert data.body == toExpect.body
    assert data.author_id == toExpect.author_id
    assert data.created_at is not None

def test_createcomment_issuenotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toCreate = CommentCreate(
        issue_id = "Invalid",
        body = "Comment 1"
    )
    r = c.post(
        "/comment/create",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toCreate.model_dump()
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.issue_not_found

def test_readcomment_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = userDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toExpect = CommentRead(
        id=commentDB.public_id,
        issue_id=commentDB.issue.public_id,
        body=commentDB.body,
        author_id=commentDB.author.public_id,
        created_at="",
        updated_at=""
    )
    r = c.get(
        f"/comment/{commentDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )
    data = CommentRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id is not None
    assert data.issue_id == toExpect.issue_id
    assert data.body == toExpect.body
    assert data.author_id == toExpect.author_id
    assert data.created_at is not None

def test_readcomment_commentnotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = userDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    invalidId = "Invalid"

    r = c.get(
        f"/comment/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.comment_not_found

def xtest_readusercomments_success(db_session):
    c = TestClient(app)
    assert False

def xtest_readusercomments_commentnotfound(db_session):
    c = TestClient(app)
    assert False

def test_editcomment_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = userDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = CommentEditIn(
        issue_id=commentDB.issue.public_id,
        body = "Comment edited by author"
    )
    toExpect = CommentEditOut(
        id=commentDB.public_id,
        issue_id=toEdit.issue_id,
        body=toEdit.body,
        author_id=commentDB.author.public_id,
        created_at="",
        updated_at=""
    )
    r = c.post(
        f"/comment/edit/{commentDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump()
    )
    data = CommentEditOut(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id == toExpect.id
    assert data.issue_id == toExpect.issue_id
    assert data.body == toExpect.body
    assert data.author_id == toExpect.author_id
    assert data.created_at is not None

def test_editcomment_commentnotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = userDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = CommentEditIn(
        issue_id=commentDB.issue.public_id,
        body = "Comment edited by author"
    )
    invalidId="Invalid"

    r = c.post(
        f"/comment/edit/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump()
    )
    
    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.comment_not_found

def test_editcomment_usernotauthor(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = anotherUserDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = CommentEditIn(
        issue_id=commentDB.issue.public_id,
        body = "Comment edited by author"
    )

    r = c.post(
        f"/comment/edit/{commentDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump()
    )

    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json()["detail"] == apiMessages.user_not_author
    
def test_deletecomment_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = userDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)

    r = c.post(
        f"/comment/delete/{commentDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == apiMessages.comment_deleted
    
def test_deletecomment_commentnotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = anotherUserDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    invalidId="Invalid"

    r = c.post(
        f"/comment/delete/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.comment_not_found
    
def test_deletecomment_usernotauthor(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.add(anotherUserDB)
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
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
        assigned=anotherUserDB
    )
    db_session.add(issueDB)
    commentDB = Comment(
        id=None,
        issue = issueDB,
        body = "Comment 1",
        author = anotherUserDB
    )
    db_session.add(commentDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)

    r = c.post(
        f"/comment/delete/{commentDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )
    
    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json()["detail"] == apiMessages.user_not_author