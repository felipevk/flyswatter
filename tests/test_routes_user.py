from fastapi.testclient import TestClient
from app.main import app
from app.api.dto import UserRead, UserCreate
from .conftest import db_session

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
    