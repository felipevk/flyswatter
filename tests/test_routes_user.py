from fastapi.testclient import TestClient
from app.main import app
from app.api.dto import UserRead, UserCreate, UserEdit
from app.db.models import User, RefreshToken
from .conftest import db_session
from fastapi import status
from app.api.routes_common import apiMessages, Token
from app.core.security import get_token_payload
from sqlalchemy import select, insert
from freezegun import freeze_time
from datetime import datetime
from app.core.config import settings

def get_test_token(client, login, password) -> Token:
    r = client.post(
        "/token",
        data={"username": login, "password": password, "grant_type": "password"}
        )

    assert r.status_code == status.HTTP_200_OK

    return Token(**r.json())


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

    assert r.status_code == status.HTTP_200_OK
    assert data.username == expectedUser.username


def test_createuser_usernameexists(db_session):
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
        email="jdoe@test.com", 
        name=toCreate.full_name, 
        pass_hash="AAAAAAA"
        ))
    db_session.commit()

    r = c.post(
        "/user/create",
        json = toCreate.model_dump())

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.username_exists
    
def test_createuser_emailexists(db_session):
    c = TestClient(app)
    toCreate = UserCreate(
        username = "jdoetestuser",
        email = "jdoetestuser@test.com",
        full_name = "John Doe Test",
        password = "secretTest"
    )
    db_session.add(User(
        id=None, 
        username="newUsername", 
        email=toCreate.email, 
        name=toCreate.full_name, 
        pass_hash="AAAAAAA"
        ))
    db_session.commit()

    r = c.post(
        "/user/create",
        json = toCreate.model_dump())

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.email_exists

def test_login_success(db_session):
    c = TestClient(app)
    login="jdoetestuser"
    password="AAAAAAA" #matches hashed
    db_session.add(User(
        id=None, 
        username=login,
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
        ))
    db_session.commit()

    data = get_test_token(c, login, password)

    assert data.access_token is not None
    assert data.refresh_token is not None
    assert data.token_type == "bearer"

def test_login_invalidusername(db_session):
    c = TestClient(app)
    login="jdoetestuser"
    password="AAAAAAA" #matches hashed
    db_session.add(User(
        id=None, 
        username="jdoe",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
        ))
    db_session.commit()

    r = c.post(
        "/token",
        data={"username": login, "password": password, "grant_type": "password"}
        )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == apiMessages.login_fail

def test_login_invalidpassword(db_session):
    c = TestClient(app)
    login="jdoetestuser"
    password="notmatch" # does not match hashed
    db_session.add(User(
        id=None, 
        username=login,
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
        ))
    db_session.commit()

    r = c.post(
        "/token",
        data={"username": login, "password": password, "grant_type": "password"}
        )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == apiMessages.login_fail

def test_readuser_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    db_session.add(userDB)
    db_session.commit()
    expectedUser = UserRead(
        id = userDB.public_id,
        username = userDB.username,
        email = userDB.email,
        full_name = userDB.name,
        admin = userDB.admin,
        disabled = userDB.disabled,
        created_at = userDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
    )
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    token = get_test_token(c, login, password)

    r = c.get(
        f"/user/{expectedUser.id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
        )
    data = UserRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id == expectedUser.id
    assert data.username == expectedUser.username
    assert data.email == expectedUser.email
    assert data.full_name == expectedUser.full_name
    assert data.admin == expectedUser.admin
    assert data.disabled == expectedUser.disabled
    assert data.created_at == expectedUser.created_at

def test_readuser_invalidtoken(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    db_session.add(userDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    invalidToken = "AAAAAAA"

    r = c.get(
        f"/user/{userDB.public_id}",
        headers={"Authorization": f"Bearer {invalidToken}"}
        )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == apiMessages.token_auth_fail

def test_readuser_expiredtoken(db_session):
    initial_datetime = datetime(year=2025, month=1, day=14,
                                        hour=12, minute=0, second=1)
    forward_datetime = initial_datetime.replace(
        minute=initial_datetime.minute + settings.auth.accessTTL + 10
        )
    with freeze_time(initial_datetime) as frozen_datetime:
        c = TestClient(app)
        userDB = User(
            id=None, 
            username="jdoetestuser",
            email="jdoetestuser@test.com",
            name= "John Doe Test",
            pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
        )
        db_session.add(userDB)
        db_session.commit()
        login = userDB.username
        password = "AAAAAAA" #matches hashed
        token = get_test_token(c, login, password)

        frozen_datetime.move_to(forward_datetime)
        r = c.get(
            f"/user/{userDB.public_id}",
            headers={"Authorization": f"Bearer {token.access_token}"}
            )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == apiMessages.token_auth_fail

def test_readuser_usernotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    db_session.add(userDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    token = get_test_token(c, login, password)
    invalidUserId = "AAAAAAA"

    r = c.get(
        f"/user/{invalidUserId}",
        headers={"Authorization": f"Bearer {token.access_token}"}
        )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.user_not_found

def test_readuser_inactiveuser(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    db_session.add(userDB)
    db_session.commit()
    expectedUser = UserRead(
        id = userDB.public_id,
        username = userDB.username,
        email = userDB.email,
        full_name = userDB.name,
        admin = userDB.admin,
        disabled = userDB.disabled,
        created_at = userDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
    )
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    token = get_test_token(c, login, password)

    userDB.disabled = True
    db_session.commit()
    r = c.get(
        f"/user/{expectedUser.id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
        )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == apiMessages.inactive_user

def test_refresh_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    db_session.add(userDB)
    db_session.commit()
    expectedUser = UserRead(
        id = userDB.public_id,
        username = userDB.username,
        email = userDB.email,
        full_name = userDB.name,
        admin = userDB.admin,
        disabled = userDB.disabled,
        created_at = userDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
    )
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    firstToken = get_test_token(c, login, password)

    r = c.post(
        "/refresh",
        params={"token": firstToken.refresh_token}
        )
    newToken = Token(**r.json())
    oldRefreshJTI = get_token_payload(firstToken.refresh_token).get("jti")
    refreshQuery = select(RefreshToken).where(RefreshToken.public_id == oldRefreshJTI)
    oldRefreshDB = db_session.execute(refreshQuery).scalars().first()

    assert r.status_code == status.HTTP_200_OK
    assert newToken.access_token is not None
    assert newToken.refresh_token is not None
    assert newToken.access_token != firstToken.access_token
    assert newToken.refresh_token != firstToken.refresh_token
    assert newToken.token_type == "bearer"
    assert oldRefreshDB.revoked_at is not None

def test_refresh_revokedfail(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    db_session.add(userDB)
    db_session.commit()
    expectedUser = UserRead(
        id = userDB.public_id,
        username = userDB.username,
        email = userDB.email,
        full_name = userDB.name,
        admin = userDB.admin,
        disabled = userDB.disabled,
        created_at = userDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
    )
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    firstToken = get_test_token(c, login, password)
    c.post(
        "/refresh",
        params={"token": firstToken.refresh_token}
        )

    r = c.post(
        "/refresh",
        params={"token": firstToken.refresh_token}
        )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == apiMessages.refresh_revoked

def test_refresh_expiredfail(db_session):
    initial_datetime = datetime(year=2025, month=1, day=14,
                                        hour=12, minute=0, second=1)
    forward_datetime = initial_datetime.replace(
        day=initial_datetime.day + settings.auth.refreshTTL + 10
        )
    with freeze_time(initial_datetime) as frozen_datetime:
        c = TestClient(app)
        userDB = User(
            id=None, 
            username="jdoetestuser",
            email="jdoetestuser@test.com",
            name= "John Doe Test",
            pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
        )
        db_session.add(userDB)
        db_session.commit()
        expectedUser = UserRead(
            id = userDB.public_id,
            username = userDB.username,
            email = userDB.email,
            full_name = userDB.name,
            admin = userDB.admin,
            disabled = userDB.disabled,
            created_at = userDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
        )
        login = userDB.username
        password = "AAAAAAA" #matches hashed
        firstToken = get_test_token(c, login, password)
        firstR = c.post(
            "/refresh",
            params={"token": firstToken.refresh_token}
            )
        token = Token(**firstR.json())

        frozen_datetime.move_to(forward_datetime)
        r = c.post(
            "/refresh",
            params={"token": token.refresh_token}
            )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == apiMessages.token_auth_fail

def test_edituser_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    newEmail = "newEmail@test.com"
    db_session.add(userDB)
    db_session.commit()
    expectedUser = UserRead(
        id = userDB.public_id,
        username = userDB.username,
        email = newEmail,
        full_name = userDB.name,
        admin = userDB.admin,
        disabled = userDB.disabled,
        created_at = userDB.created_at.strftime('%a %d %b %Y, %I:%M%p')
    )
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    token = get_test_token(c, login, password)
    toEdit = UserEdit(
        id = userDB.public_id,
        username = userDB.username,
        email = newEmail,
        full_name = userDB.name,
        password = password,
        admin = userDB.admin,
        disabled = userDB.disabled
    )

    r = c.post(
        "/user/edit",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json = toEdit.model_dump()
        )
    data = UserRead(**r.json())

    assert r.status_code == status.HTTP_200_OK
    assert data.id == expectedUser.id
    assert data.username == expectedUser.username
    assert data.email == expectedUser.email
    assert data.full_name == expectedUser.full_name
    assert data.admin == expectedUser.admin
    assert data.disabled == expectedUser.disabled
    assert data.created_at == expectedUser.created_at

def test_edituser_usernotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    newEmail = "newEmail@test.com"
    db_session.add(userDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    token = get_test_token(c, login, password)
    toEdit = UserEdit(
        id = "AAAAA", # invalid id
        username = userDB.username,
        email = newEmail,
        full_name = userDB.name,
        password = password,
        admin = userDB.admin,
        disabled = userDB.disabled
    )

    r = c.post(
        "/user/edit",
        headers={"Authorization": f"Bearer {token.access_token}"},
        json = toEdit.model_dump()
        )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == apiMessages.user_not_found

def test_deleteuser_success(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    newEmail = "newEmail@test.com"
    db_session.add(userDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    token = get_test_token(c, login, password)

    r = c.post(
        f"/user/delete/{userDB.public_id}",
        headers={"Authorization": f"Bearer {token.access_token}"}
        )

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == apiMessages.user_deleted

def test_deleteuser_usernotfound(db_session):
    c = TestClient(app)
    userDB = User(
        id=None, 
        username="jdoetestuser",
        email="jdoetestuser@test.com",
        name= "John Doe Test",
        pass_hash="$2b$12$C/ZIa0h6IbTLG0aR1lkzCu0S26wbELjeNkFv/frObFmuVYrBPkgzO"
    )
    newEmail = "newEmail@test.com"
    db_session.add(userDB)
    db_session.commit()
    login = userDB.username
    password = "AAAAAAA" #matches hashed
    token = get_test_token(c, login, password)
    invalidId = "AAAA"

    r = c.post(
        f"/user/delete/{invalidId}",
        headers={"Authorization": f"Bearer {token.access_token}"}
        )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] != apiMessages.user_not_found