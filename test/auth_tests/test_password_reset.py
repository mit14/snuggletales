import pytest
from app import models

MAIN_URL = "/api/dev/v1/user/"
FORGOT_PASSWORD_OTP = MAIN_URL + "forgot_password_otp"
RESET_PASSWORD =  MAIN_URL + "reset_password"
UPDATE_PASSWORD = MAIN_URL + "update_password"


def test_forgot_password_otp_success(verifed_test_user, client, session, mock_send_email):
    res = client.post(FORGOT_PASSWORD_OTP,
                      json={'email': verifed_test_user['email']})
    assert res.status_code == 201
    assert res.json()['detail'] == 'OTP sent to your email'


def test_reset_password_success(verifed_test_user, client, session, mock_send_email):
    res = client.post(FORGOT_PASSWORD_OTP,
                      json={'email': verifed_test_user['email']}) 

    user_id = verifed_test_user['user_id']
    otp = session.query(models.ResetPasswordOTP).filter(models.ResetPasswordOTP.user_id  == user_id).first()
    data = {
        'email': verifed_test_user['email'],
        'new_password': 'password123',
        'otp': otp.otp
    }

    res = client.post(RESET_PASSWORD, json= data)
    assert res.status_code == 201
    assert res.json()['detail'] == "Password changed, please login."


def test_forgot_password_wrong_email(verifed_test_user, client, session, mock_send_email):
    res = client.post(FORGOT_PASSWORD_OTP,
                      json={'email': "test123@wrongemail.com"})
    assert res.status_code == 404
    assert res.json()['detail'] == 'User not found'


def test_reset_password_wrong_email(verifed_test_user, client, session, mock_send_email):
    res = client.post(FORGOT_PASSWORD_OTP,
                      json={'email': verifed_test_user['email']}) 

    user_id = verifed_test_user['user_id']
    otp = session.query(models.ResetPasswordOTP).filter(models.ResetPasswordOTP.user_id  == user_id).first()
    data = {
        'email': "test123@wrongemail.com",
        'new_password': 'password123',
        'otp': otp.otp
    }

    res = client.post(RESET_PASSWORD, json= data)
    assert res.status_code == 404
    assert res.json()['detail'] == "User not found"


def test_reset_password_wrong_otp(verifed_test_user, client, session, mock_send_email):
    res = client.post(FORGOT_PASSWORD_OTP,
                      json={'email': verifed_test_user['email']}) 

    user_id = verifed_test_user['user_id']
    otp = session.query(models.ResetPasswordOTP).filter(models.ResetPasswordOTP.user_id  == user_id).first()
    data = {
        'email': verifed_test_user['email'],
        'new_password': 'password123',
        'otp': "890789"
    }

    res = client.post(RESET_PASSWORD, json= data)
    assert res.status_code == 400
    assert res.json()['detail'] == "Invalid OTP or OTP expired"


def test_update_password_success(verifed_test_user, client, session, mock_send_email):
    data = {
        'email': verifed_test_user['email'],
        'old_password': verifed_test_user['password'],
        'new_password': 'password123'
    }
    res = client.post(UPDATE_PASSWORD, json=data)
    assert res.status_code == 201
    assert "access_token" in res.json()



def test_update_password_not_success(verifed_test_user, client, session, mock_send_email):
    data = {
        'email': verifed_test_user['email'],
        'old_password': "asudohfuhsadf",
        'new_password': 'password123'
    }
    res = client.post(UPDATE_PASSWORD, json=data)
    assert res.status_code == 403
    assert res.json()['detail'] == "Invalid Credentials"