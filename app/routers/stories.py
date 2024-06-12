from typing import List, Optional
from fastapi import  status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Session
from app import database, utils, schemas, models, oauth2



router = APIRouter(prefix= "/api/dev/v1/story",
                   tags= ["Getting stories"]
                   )



@router.get("/all", response_model=schemas.StoriesResponse)
def get_all_stories(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):

    # Fetch all stories sorted by created date
    user_liked_story_ids = [liked_story.story_id for liked_story in db.query(models.LikedStory.story_id).filter(models.LikedStory.user_id == current_user.id).all()]

    stories = (
        db.query(models.Story, func.count(models.LikedStory.story_id).label("likes"))
        .join(models.LikedStory, models.LikedStory.story_id == models.Story.story_id, isouter=True)
        .group_by(models.Story.story_id)
        .order_by(models.Story.created_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )

    all_stories_result = [
        {
            "story_id": story.story_id,
            "title": story.title,
            "description": story.description,
            "title_image_path": story.title_image_path,
            "likes": likes,
            "is_liked": story.story_id in user_liked_story_ids
        }
        for story, likes in stories
    ]

    if skip != 0:
        return {
            "all_stories": all_stories_result
        }

    top_rated_stories = (
        db.query(models.Story, func.count(models.LikedStory.story_id).label("likes"))
        .join(models.LikedStory, models.LikedStory.story_id == models.Story.story_id, isouter=True)
        .group_by(models.Story.story_id)
        .order_by(func.count(models.LikedStory.story_id).desc())
        .limit(5)
        .all()
    )

    top_rated_stories_result = [
        {
            "story_id": story.story_id,
            "title": story.title,
            "description": story.description,
            "title_image_path": story.title_image_path,
            "likes": likes,
            "is_liked": story.story_id in user_liked_story_ids
        }
        for story, likes in top_rated_stories
    ]

    return {
        "all_stories": all_stories_result,
        "top_rated_stories": top_rated_stories_result
    }


@router.get("/search", response_model=List[schemas.UserStoryOut])
def search_story(db: Session = Depends(database.get_db),current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: str = ""):
    user_liked_story_ids = [liked_story.story_id for liked_story in db.query(models.LikedStory.story_id).filter(models.LikedStory.user_id == current_user.id).all()]
    
    stories = (
        db.query(models.Story, func.count(models.LikedStory.story_id).label("likes"))
        .join(models.LikedStory, models.LikedStory.story_id == models.Story.story_id, isouter=True)
        .group_by(models.Story.story_id)
        .filter(models.Story.description.contains(search))
        .order_by(models.Story.created_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )

    all_stories_result = [
        {
            "story_id": story.story_id,
            "title": story.title,
            "description": story.description,
            "title_image_path": story.title_image_path,
            "likes": likes,
            "is_liked": story.story_id in user_liked_story_ids
        }
        for story, likes in stories
    ]

    return all_stories_result


@router.get("/{story_id}", response_model=schemas.UserPageOut)
def get_story(story_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    read_story_entry = db.query(models.ReadStory).filter_by(user_id=current_user.id, story_id=story_id).first()

    if not read_story_entry:
        new_read_story = models.ReadStory(user_id=current_user.id, story_id=story_id)
        db.add(new_read_story)
        db.commit()

    read_page_entry = (
        db.query(models.Pages)
        .join(models.ReadPage, models.ReadPage.page_id == models.Pages.page_id)
        .filter(models.ReadPage.user_id == current_user.id, models.Pages.story_id == story_id)
        .order_by(models.ReadPage.read_at.desc())
        .first()
    )

    if read_page_entry:
        last_read_page = read_page_entry.page_id
    else:
        last_read_page = (
            db.query(models.Pages)
            .filter_by(story_id=story_id)
            .order_by(models.Pages.page_number)
            .first()
            .page_id
        )
    
    page = db.query(models.Pages).filter_by(page_id = last_read_page).first()
    story = db.query(models.Story).filter_by(story_id=story_id).first()

    has_next_page = db.query(models.Pages).filter_by(story_id=story_id, page_number=page.page_number + 1).first() is not None
    
    return {
        "story_id": story.story_id,
        "story_title": story.title,
        "page_id": page.page_id,
        "content": page.content,
        "page_number": page.page_number,
        "has_next_page": has_next_page
    }


@router.post("/{story_id}/next/{current_page_id}", response_model=schemas.UserPageOut)
def next_page(story_id: int, current_page_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    current_page = db.query(models.Pages).filter_by(page_id=current_page_id, story_id=story_id).first()
    next_page = db.query(models.Pages).filter_by(story_id=story_id, page_number=current_page.page_number + 1).first()

    if not next_page:
        raise HTTPException(status_code=404, detail="Next page not found")

    has_next_page = db.query(models.Pages).filter_by(story_id=story_id, page_number=next_page.page_number + 1).first() is not None

    db.query(models.ReadPage).filter_by(user_id=current_user.id, page_id=current_page_id).delete()
    db.add(models.ReadPage(user_id=current_user.id, page_id=next_page.page_id))
    db.commit()

    story = db.query(models.Story).filter_by(story_id=story_id).first()

    return {
        "story_id": story.story_id,
        "story_title": story.title,
        "page_id": next_page.page_id,
        "content": next_page.content,
        "page_number": next_page.page_number,
        "has_next_page": has_next_page
    }

