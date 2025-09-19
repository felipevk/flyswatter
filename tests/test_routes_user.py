from fastapi.testclient import TestClient
from app.main import app
from app.api.dto import UserRead, UserCreate
from app.db.models import User
from .conftest import db_session
from fastapi import status
from app.api.routes_common import apiMessages

def test_createuser_success():
    c = TestClient(app)
    toCreate = UserCreate(
        username = "jdoetestuser",
        email = "jdoetestuser@test.com",
        full_name = "John Doe Test",
        password = "secretTest"
    )
    expectedUser = UserRead(
        id = "",
        username = "jdoetestuser",
        email = "jdoetestuser@test.com",
        full_name = "John Doe Test",
        admin = False,
        disabled = False,
        created_at = ""
    )

    r = c.post(
        "/user/create",
        json = toCreate.model_dump())
    data = UserRead(**r.json())

    assert r.status_code == 200
    assert data.username == expectedUser.username


def test_createuser_exists(db_session):
    c = TestClient(app)
    toCreate = UserCreate(
        username = "jdoetestuser",
        email = "jdoetestuser@test.com",
        full_name = "John Doe Test",
        password = "secretTest"
    )
    db_session.add(User(
        id=None, 
        username=toCreate.username, 
        email=toCreate.email, 
        name=toCreate.full_name, 
        pass_hash="AAAAAAA"
        ))
    db_session.commit()

    r = c.post(
        "/user/create",
        json = toCreate.model_dump())

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.username_exists

        
    