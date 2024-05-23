from sqlalchemy import TIMESTAMP, Boolean, Column, DateTime, ForeignKey, Integer, String, create_engine, text, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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
    role = Column(String(50), default='user')

    otps = relationship('ResetPasswordOTP', back_populates= "user")
    liked_stories = relationship("LikedStory", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    read_stories = relationship("ReadStory", back_populates="user")
    read_pages = relationship("ReadPage", back_populates="user")
    

class ResetPasswordOTP(Base):
    __tablename__ = "reset_password_otp"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete= "CASCADE") , nullable= False)
    expires_at = Column(DateTime, nullable=False)
    otp = Column(String(6), nullable=False)
    user = relationship('User', back_populates="otps")


class Story(Base):
    __tablename__ = "stories"

    story_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable= False)
    title_image_path = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    pages = relationship("Pages", back_populates="story")
    liked_by = relationship("LikedStory", back_populates="story")
    categories = relationship("StoryCategory", back_populates="story")
    read_by = relationship("ReadStory", back_populates="story")


class Pages(Base):
    __tablename__ = "pages"

    page_id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.story_id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    image_path = Column(String(255)) 
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    story = relationship("Story", back_populates="pages")
    audio_files = relationship("AudioFile", back_populates="page")
    read_by = relationship("ReadPage", back_populates="page")


class AudioFile(Base):
    __tablename__ = "audio_files"
    
    audio_id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.page_id", ondelete="CASCADE"), nullable=False)
    audio_path = Column(String(255), nullable=False)
    duration = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    page = relationship("Pages", back_populates="audio_files")


class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    stories = relationship("StoryCategory", back_populates="category")


class StoryCategory(Base):
    __tablename__ = "story_categories"
    
    story_id = Column(Integer, ForeignKey("stories.story_id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), primary_key=True)

    story = relationship("Story", back_populates="categories")
    category = relationship("Category", back_populates="stories")


class LikedStory(Base):
    __tablename__ = "liked_stories"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    story_id = Column(Integer, ForeignKey("stories.story_id", ondelete="CASCADE"), primary_key=True)
    liked_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="liked_stories")
    story = relationship("Story", back_populates="liked_by")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    subscription_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_type = Column(String(50))  # e.g., 'monthly', 'yearly'
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP)
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())

    user = relationship("User", back_populates="subscriptions")

class ReadStory(Base):
    __tablename__ = "read_stories"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    story_id = Column(Integer, ForeignKey("stories.story_id", ondelete="CASCADE"), primary_key=True)
    started_at = Column(TIMESTAMP, server_default=func.now())
    finished_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="read_stories")
    story = relationship("Story", back_populates="read_by")


class ReadPage(Base):
    __tablename__ = "read_pages"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    page_id = Column(Integer, ForeignKey("pages.page_id", ondelete="CASCADE"), primary_key=True)
    read_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="read_pages")
    page = relationship("Pages", back_populates="read_by")