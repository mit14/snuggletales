from typing import List
from fastapi import  status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from sqlalchemy import case, func
from sqlalchemy.orm import Session
from app import database, utils, schemas, models, oauth2



router = APIRouter(prefix= "/api/dev/v1/user",
                   tags= ["User history"]
                   )



@router.get("/history", response_model=List[schemas.UserLikedStoryOut])
def get_user_read_history(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: str = ""):
    # Ensure current_user is valid
    if not current_user:
        raise HTTPException(status_code=401, detail="User authentication required")


    subquery = (
        db.query(
            models.LikedStory.story_id,
            func.count('*').label('likes')
        )
        .group_by(models.LikedStory.story_id)
        .subquery()
    )
    
    history = (
        db.query(models.Story, models.ReadStory, subquery.c.likes)
        .join(models.ReadStory, models.Story.story_id == models.ReadStory.story_id)
        .outerjoin(subquery, models.Story.story_id == subquery.c.story_id)
        .filter(models.ReadStory.user_id == current_user.id, models.Story.description.contains(search))
        .order_by(models.ReadStory.started_at.asc())
        .limit(limit)
        .offset(skip)
        .all()
    )

    user_history = [
        schemas.UserLikedStoryOut(
            story_id=story.story_id,
            title=story.title,
            title_image_path=story.title_image_path,
            likes=likes or 0,  
            is_liked=(story.story_id in [liked.story_id for liked in db.query(models.LikedStory.story_id).filter(models.LikedStory.user_id == current_user.id).all()])
        ) for story, read_story, likes in history
    ]

    return user_history