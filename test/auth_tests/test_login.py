from fastapi import status
import pytest
from jose import jwt
from app import utils, models, schemas
from app.config import settings

MAIN_URL = "/api/dev/v1/user/"
REGISTER = MAIN_URL + "register/"
LOGIN = MAIN_URL + "login/"



def test_login_user_not_verified(test_user, client):
    res = client.post(
        LOGIN, data={"username": test_user['email'], "password": test_user['password']}
    )
    
    assert res.status_code == 401
    res = res.json()
    assert res['detail'] ==  'User not verified, please verify.'


def test_login_user_verified(verifed_test_user, client):
    res = client.post(
        LOGIN, data={"username": verifed_test_user['email'], "password": verifed_test_user['password']}
    )

    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=settings.algorithm)
    id = payload.get('user_id')
    print(id)

    assert id == verifed_test_user['user_id']


@pytest.mark.parametrize("email, password, status_code", [
    ('wrong@email.com', 'password123', 403),
    ('test@gmail.com', 'wrongpassword', 403),
    ('wrongemail', 'wrongpassword', 403),
    (None, 'password123', 422),
    ('test@gmail.com', None, 422)
])
def test_login_invalid_credentials(test_user, client, email, password, status_code):
    res = client.post(
        LOGIN, data={"username": email, "password": password}
    )

    assert res.status_code == status_code


