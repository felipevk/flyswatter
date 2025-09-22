from fastapi import status

from app.api.routes_common import Token


def get_test_token(client, login, password) -> Token:
    r = client.post(
        "/token",
        data={"username": login, "password": password, "grant_type": "password"},
    )

    assert r.status_code == status.HTTP_200_OK

    return Token(**r.json())