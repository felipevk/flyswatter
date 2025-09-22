from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import insert, select

from app.api.dto import ProjectCreate, ProjectEdit, ProjectRead
from app.api.routes_common import Token, apiMessages
from app.core.config import settings
from app.db.models import Project, User
from app.main import app

from .conftest import db_session

from .test_routes_common import *

def test_createproject_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toCreate = ProjectCreate(
        title="Test Project",
        key="PROJ"
    )
    toExpect = ProjectRead(
        title=toCreate.title,
        key=toCreate.key,
        id="",
        author=userDB.username,
        created_at=""
    )

    r = c.post(
        "/project/create",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toCreate.model_dump()
    )
    data = ProjectRead(**r.json())
    
    assert r.status_code == status.HTTP_200_OK
    assert data.title == toExpect.title
    assert data.author == toExpect.author
    assert data.key == toExpect.key

def test_createproject_keyexists(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toCreate = ProjectCreate(
        title=projectDB.title,
        key=projectDB.key
    )

    r = c.post(
        "/project/create",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toCreate.model_dump()
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.projectkey_exists

def test_createproject_usernotadmin(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toCreate = ProjectCreate(
        title="Test Project",
        key="PROJ"
    )

    r = c.post(
        "/project/create",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toCreate.model_dump()
    )

    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json()["detail"] == apiMessages.requires_admin
    

def test_readproject_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toExpect = ProjectRead(
        title=projectDB.title,
        key=projectDB.key,
        id="",
        author=userDB.username,
        created_at=""
    )

    r = c.get(
        f"/project/{projectDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )
    data = ProjectRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.title == toExpect.title
    assert data.author == toExpect.author
    assert data.key == toExpect.key

def test_readproject_projectnotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    invalidId = "P"

    r = c.get(
        f"/project/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.project_not_found

def test_readuserprojects_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.add(
        Project(
            id=None,
            title="Test Project",
            key="PROJ",
            author=userDB
        )
    )
    db_session.add(
        Project(
            id=None,
            title="Another Project",
            key="ANOT",
            author=userDB
        )
    )
    anotherUserDB = User(
        id=None,
        username="anotheruser",
        email="anotheruser@test.com",
        name="Another User",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    db_session.add(anotherUserDB)
    db_session.add(
        Project(
            id=None,
            title="Test Project 2",
            key="TPRO",
            author=anotherUserDB
        )
    )
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toExpect = [
        ProjectRead(
            title="Test Project",
            key="PROJ",
            id="",
            author=userDB.username,
            created_at=""
        ),
        ProjectRead(
            title="Another Project",
            key="ANOT",
            id="",
            author=userDB.username,
            created_at=""
        )
    ]

    r = c.get(
        f"/project/mine",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )
    data = [ProjectRead.model_validate(d) for d in r.json()]

    assert r.status_code == status.HTTP_200_OK
    assert len(data) == len(toExpect)
    for project, expected in zip(data, toExpect):
        assert project.title == expected.title
        assert project.author == expected.author
        assert project.key == expected.key
        
def test_editproject_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = ProjectEdit(
        title="Test Project NEW",
        key=projectDB.key,
        id=projectDB.public_id,
        author=userDB.username,
        created_at=""
    )
    toExpect = ProjectRead(
        title=toEdit.title,
        key=toEdit.key,
        id="",
        author=toEdit.author,
        created_at=""
    )

    r = c.post(
        "/project/edit",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump()
    )
    data = ProjectRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.title == toExpect.title
    assert data.author == toExpect.author
    assert data.key == toExpect.key

def test_editproject_projectnotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = ProjectEdit(
        title="Test Project NEW",
        key=projectDB.key,
        id="Invalid",
        author=userDB.username,
        created_at=""
    )

    r = c.post(
        "/project/edit",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump()
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.project_not_found

def test_editproject_usernotadmin(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    toEdit = ProjectEdit(
        title="Test Project NEW",
        key=projectDB.key,
        id=projectDB.public_id,
        author=userDB.username,
        created_at=""
    )
    toExpect = ProjectRead(
        title=toEdit.title,
        key=toEdit.key,
        id="",
        author=toEdit.author,
        created_at=""
    )

    r = c.post(
        "/project/edit",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json=toEdit.model_dump()
    )
    
    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json()["detail"] == apiMessages.requires_admin
    
def test_deleteproject_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)

    r = c.post(
        f"/project/delete/{projectDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == apiMessages.project_deleted
    
def test_deleteproject_projectnotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=True
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)
    invalidId = "Invalid"

    r = c.post(
        f"/project/delete/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.project_not_found

def test_deleteproject_usernotadmin(db_session):
    c = TestClient(app)
    userDB = User(
        id=None,
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name="John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO",
        admin=False
    )
    db_session.add(userDB)
    db_session.commit()
    projectDB = Project(
        id=None,
        title="Test Project",
        key="PROJ",
        author=userDB
    )
    db_session.add(projectDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA"  # matches hashed
    token = get_test_token(c, login, password)

    r = c.post(
        f"/project/delete/{projectDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
    )
    
    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json()["detail"] == apiMessages.requires_admin
