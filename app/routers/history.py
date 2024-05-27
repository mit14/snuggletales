from typing import List
from fastapi import  status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app import database, utils, schemas, models, oauth2



router = APIRouter(prefix= "/api/dev/v1/story",
                   tags= ["Strory Like"]
                   )


# @router.get("/history", response_model=schemas.UserLikedStoryOut)
# def get_user_read_histoy(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):

#     user_history = 