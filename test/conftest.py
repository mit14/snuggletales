from fastapi.testclient import TestClient
from fastapi import status
import pytest
from app.main import app
from app import models, utils, schemas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.database import Base
from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = f"postgresql://mitpatel:Password123@localhost/snuggle_tales_test_env"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

EMAIL = "test_user@example.com"
PASSWORD = "password123"
MAIN_URL = "/api/dev/v1/user/"
REGISTER = MAIN_URL + "register/"
VERIFY = MAIN_URL + "verify/"


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def mock_send_email(mocker):
    return mocker.patch('app.utils.send_email')


@pytest.fixture
def test_user(client, mock_send_email):
    user_data = {
        "email": EMAIL,
        "password": PASSWORD,
        "age": 25
    }

    res = client.post(REGISTER, json=user_data)
    assert res.status_code == status.HTTP_201_CREATED
    mock_send_email.assert_called_once()

    new_user = res.json()
    new_user['password'] = PASSWORD
    return new_user


@pytest.fixture
def verifed_test_user(test_user, client, session):
    user_id = test_user['id']
    # utils.delete_otp(user_id, session)

    otp = utils.store_otp(session, user_id)
    
    otp_validation = {
        "email": EMAIL,
        "otp": str(otp)
    }
    token = client.post(VERIFY, json=otp_validation)
    # print(token)
    # new_verified_user = token.json()

    new_verified_user = token.json()

    new_verified_user['email'] = EMAIL
    new_verified_user['password'] = PASSWORD
    new_verified_user['user_id'] = user_id

    return new_verified_user


