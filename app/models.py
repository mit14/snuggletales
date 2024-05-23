from sqlalchemy import TIMESTAMP, Boolean, Column, DateTime, ForeignKey, Integer, String, create_engine, text
from sqlalchemy.orm import relationship

from datetime import datetime, timezone
from .database import Base, engine



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    age = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=True, unique=True)
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    is_verified = Column(Boolean, default=False, nullable= False)
    otps = relationship('ResetPasswordOTP', back_populates= "user")


class ResetPasswordOTP(Base):
    __tablename__ = "reset_password_otp"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete= "CASCADE") , nullable= False)
    expires_at = Column(DateTime, nullable=False)
    otp = Column(String(6), nullable=False)
    user = relationship('User', back_populates="otps")

