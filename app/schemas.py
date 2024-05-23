from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    age: int
    phone_number: Optional[int] = None

class UserOut(BaseModel):
     id: int
     email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class OTPValidation(PasswordResetRequest):
    otp: str


class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str
    otp: str

class PasswordUpdate(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class GoogleToken(BaseModel):
    token: str


class CreateStory(BaseModel):
    title: str
    description: str
    title_image_path: Optional[str]


class CreatePage(BaseModel):
    page_number: int
    content: str
    image_path: str

class AdminStroyOut(BaseModel):
    story_id: int
    title: str
    description: str
    title_image_path: str

class AdminPageOut(BaseModel):
    page_id: int
    story_id: int
    page_number: int
    content: str
    image_path: str
    
    
