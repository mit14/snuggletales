from typing import List
from fastapi import  status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app import database, utils, schemas, models, oauth2



router = APIRouter(prefix= "/api/dev/v1/story",
                   tags= ["Strory Like"]
                   )



@router.post("/like", status_code=status.HTTP_201_CREATED)
def like_story(like: schemas.UserStoryLike, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):

    valid_story = db.query(models.Story).filter(models.Story.story_id == like.story_id).all()
    
    if not valid_story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Stroy with id: {like.story_id} was not found.")

    like_query = db.query(models.LikedStory).filter(models.LikedStory.story_id == like.story_id, models.LikedStory.user_id == current_user.id)
    found_like = like_query.first()
    
    if found_like and like.dir == 0:
        like_query.delete()
        db.commit()
        return {"detail": "Successffully deleted like."}
    elif not found_like and like.dir == 1:
        new_like = models.LikedStory(user_id = current_user.id, story_id= like.story_id)
        db.add(new_like)
        db.commit()
        return {"detail": "Successfully Liked the story."}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Please check story_id and like dir.")


@router.get("/user_liked", response_model=List[schemas.UserLikedStoryOut])
def get_liked_stories_by_user(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):
 
    liked_stories = (
        db.query(models.Story)
        .join(models.LikedStory, models.LikedStory.story_id == models.Story.story_id)
        .filter(models.LikedStory.user_id == current_user.id)
        .order_by(models.LikedStory.liked_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )

    result = [
        {
            "story_id": story.story_id,
            "title": story.title,
            "description": story.description,
            "title_image_path": story.title_image_path
        }
        for story in liked_stories
    ]

    return result