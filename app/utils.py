from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from aiosmtplib import send
from email.message import EmailMessage
from app.models import ResetPasswordOTP
import random
import string


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

########################################  SEND OTP EMAIL  ###########################################

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = "kmpinnovations@outlook.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await send(
        message,
        hostname="smtp-mail.outlook.com",
        port=587,
        username="kmpinnovations@outlook.com",
        password="Khiara@15072022",
        start_tls=True,
    )


########################################  GENERATE, STORE, DELETE OTP ###########################################

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def store_otp(db: Session, user_id: int):
    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)  # OTP valid for 10 minutes
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