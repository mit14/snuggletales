from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Null


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
    audio_file: Optional[str] = "test"

class AdminStroyOut(BaseModel):
    story_id: int
    title: str
    description: str
    title_image_path: str

class AdminPageOut(BaseModel):
    # page_id: int
    story_id: int
    page_number: int
    content: str
    image_path: str
    audio_path: str


class UserStoryOut(BaseModel):
    story_id: int
    title: str
    description: str
    title_image_path: str
    likes: int
    is_liked: bool

    class Config:
        orm_mode = True


class StoriesResponse(BaseModel):
    all_stories: List[UserStoryOut]
    top_rated_stories: Optional[List[UserStoryOut]] = []


class UserStoryLike(BaseModel):
    story_id: int
    dir: int = Field(..., ge=-1, le=1)
    
class UserLikedStoryOut(BaseModel):
    story_id: int
    title: str
    title_image_path: str
    likes: int
    is_liked: bool

class UserPageOut(BaseModel):
    story_id: int
    story_title: str
    page_id: int
    content: str
    page_number: int
    has_next_page: bool

    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    age: Optional[str] = None
    phone_number: Optional[str] = None
    