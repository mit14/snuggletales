from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from aiosmtplib import send
from email.message import EmailMessage
from app.models import ResetPasswordOTP, User
from app.oauth2 import get_current_user
import random
import string
from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

########################################  SEND OTP EMAIL  ###########################################

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.email_otp
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await send(
        message,
        hostname="smtp-mail.outlook.com",
        port=587,
        username=settings.email_otp,
        password=settings.epwd,
        start_tls=True,
    )
    

########################################  GENERATE, STORE, DELETE OTP ###########################################

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def store_otp(db: Session, user_id: int):
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=30)  
    otp_record = ResetPasswordOTP(user_id=user_id, otp=otp, expires_at=expires_at)
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)
    return otp


def validate_otp(db: Session, user_id: int, otp: str):
    otp_record = db.query(ResetPasswordOTP).filter_by(user_id=user_id, otp=otp).first()
    if otp_record and otp_record.expires_at > datetime.utcnow():
        return True
    return False


def delete_otp(user_id, db: Session):
    db.query(ResetPasswordOTP).filter(ResetPasswordOTP.user_id == user_id).delete()
    db.commit()


########################################  CREATE AND VERIFY HASH  ###########################################

def hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

