from fastapi import status
from app import utils, models, schemas

MAIN_URL = "/api/dev/v1/user/"
REGISTER = MAIN_URL + "register/"
VERIFY = MAIN_URL + "verify/"



def test_create_user_success(client, mock_send_email):

    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "age": 25  
    }
    res = client.post(REGISTER, json= user_data )
    new_user = schemas.UserOut(**res.json())

    assert new_user.email == "test@example.com"
    assert res.status_code == 201
    

def test_create_user_email_already_registered(client, session, mock_send_email):

    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "age": 25
    }

    client.post(REGISTER, json=user_data)
    res = client.post(REGISTER, json=user_data)

    assert res.status_code == 400
    data = res.json()
    assert data["detail"] == "Email already registered"  


def test_verify_user_success(client ,session , mock_send_email):

    user_data = {
        "email": "verifytest@example.com",
        "password": "password123",
        "age": 25
    }

    res = client.post(REGISTER, json=user_data)
    assert res.status_code == status.HTTP_201_CREATED
    mock_send_email.assert_called_once()


    user_id = res.json()['id']

    utils.delete_otp(user_id, session)

    otp = utils.store_otp(session, user_id)
    
    otp_record = session.query(models.ResetPasswordOTP).filter(models.ResetPasswordOTP.user_id  == user_id).first()
    assert otp_record is not None
    assert otp_record.otp == otp

    otp_validation = {
        "email": user_data["email"],
        "otp": str(otp)
    }
    res = client.post(VERIFY, json=otp_validation)
    assert res.status_code == 202
    data = res.json()
    assert "access_token" in data


def test_verify_user_not_successfull(client ,session , mock_send_email):

    user_data = {
        "email": "verifytest@example.com",
        "password": "password123",
        "age": 25
    }

    res = client.post(REGISTER, json=user_data)
    assert res.status_code == status.HTTP_201_CREATED
    mock_send_email.assert_called_once()


    user_id = res.json()['id']

    utils.delete_otp(user_id, session)

    otp = utils.store_otp(session, user_id)
    
    otp_record = session.query(models.ResetPasswordOTP).filter(models.ResetPasswordOTP.user_id  == user_id).first()
    assert otp_record is not None
    assert otp_record.otp == otp

    otp_validation = {
        "email": user_data["email"],
        "otp": "98327480"
    }
    res = client.post(VERIFY, json=otp_validation)
    assert res.status_code == 400
    data = res.json()
    assert data['detail'] == "Invalid OTP or OTP expired"


def test_verify_user_already_verified(client ,session , mock_send_email):

    user_data = {
        "email": "verifytest@example.com",
        "password": "password123",
        "age": 25
    }

    res = client.post(REGISTER, json=user_data)
    assert res.status_code == status.HTTP_201_CREATED
    mock_send_email.assert_called_once()


    user_id = res.json()['id']

    utils.delete_otp(user_id, session)

    otp = utils.store_otp(session, user_id)
    
    otp_record = session.query(models.ResetPasswordOTP).filter(models.ResetPasswordOTP.user_id  == user_id).first()
    assert otp_record is not None
    assert otp_record.otp == otp

    otp_validation = {
        "email": user_data["email"],
        "otp": str(otp)
    }
    res = client.post(VERIFY, json=otp_validation)
    assert res.status_code == 202

    res = client.post(VERIFY, json=otp_validation)
    assert res.status_code == 409
    data = res.json()
    assert data['detail'] == "User already Verified"





