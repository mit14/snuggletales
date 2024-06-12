from typing import List
from fastapi import  Response, status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from loguru import logger

from app import database, utils, schemas, models, oauth2


router = APIRouter(prefix= "/admin/dev/api",
                   tags= ["Create Stories and Pages"] 
                   )



###############################################################  LOGIN  ##################################################################################################

@router.post("/login", response_model= schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        logger.warning(f"Falied login as admin (User not found): {user.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    if user.role != "admin":
        logger.warning(f"Falied login as admin (User role is not admin): {user.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Not authorized")
    
    if not utils.verify_password(user_credentials.password, user.password):
        logger.warning(f"Falied login as admin, cannot verify password: {user.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={"user_id":user.id})
    logger.info(f"Admin login successful. {user.id}")
    return {"access_token": access_token, "token_type": "bearer"}



########################################################  Create Story  ##################################################################################################

@router.post("/story")
def create_story(story: schemas.CreateStory, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user) ):

    new_story = models.Story(**story.model_dump())
    db.add(new_story)
    db.commit()
    db.refresh(new_story)

    logger.info(f'Story added successfully. Story id: {new_story.story_id}, Story title: {new_story.title}, created by: {current_user.id}')
    
    return {"detail": "Story added successfully"}



#####################################################  Get All Stories  ##################################################################################################

@router.get("/story", response_model=List[schemas.AdminStroyOut])
def get_all_stories(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user)):
    
    stories = db.query(models.Story).all()
    logger.info(f"User {current_user.id} requested all stories.")
    return stories



#########################################################  Create Page  ##################################################################################################

@router.post("/{story_id}/page")
def create_page(story_id: int, page: schemas.CreatePage, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user) ):

    story_query = db.query(models.Story).filter(models.Story.story_id == story_id)
    story = story_query.first()

    if story == None:
        logger.warning(f"Story with the id: {story_id} was not found. User: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Story with the id: {story_id} was not found.')
    
    existing_page = db.query(models.Pages).filter(models.Pages.story_id == story_id, models.Pages.page_number == page.page_number).first()
    
    if existing_page:
        logger.warning(f"Page number {page.page_number} already exists for story with id: {story_id}. User: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Page number {page.page_number} already exists for story with id: {story_id}.")
    
    # new_page = models.Pages(story_id= story_id, **page.model_dump())
    new_page = models.Pages(
        story_id= story_id,
        page_number = page.page_number,
        content = page.content,
        image_path = page.image_path
        )
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    audio_file = models.AudioFile(
        page_id = new_page.page_id,
        audio_path = page.audio_file,

    )
    db.add(audio_file)
    db.commit()
    db.refresh(audio_file)
    logger.info(f"Page number: {new_page.page_number} added for Story: {story.title} by {current_user.id}")
    return {"detail": "Page added successfully"}


################################################  Get Pages of a Story  ##################################################################################################

@router.get("/{story_id}/page", response_model=List[schemas.AdminPageOut])
def get_pages(story_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user)):
    
    pages_query = (
        db.query(models.Pages, models.AudioFile.audio_path)
        .join(models.AudioFile, models.Pages.page_id == models.AudioFile.page_id, isouter=True)
        .filter(models.Pages.story_id == story_id)
        .all()
    )
    
    result = [
        {
        'story_id': page.Pages.story_id,
        'page_number': page.Pages.page_number,
        'content': page.Pages.content,
        'image_path': page.Pages.image_path,
        'audio_path': page.audio_path if page.audio_path else None
    } for page in pages_query
    ]
    logger.info(f"User {current_user.id} requested all pages for story {story_id}.")
    return result




#######################################################  Delete Story  ##################################################################################################


@router.delete('/{story_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_story(story_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user)):
    
    story_query = db.query(models.Story).filter(models.Story.story_id == story_id)
    story = story_query.first()


    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Story with the id: {story_id} was not found.')

    story_query.delete()
    db.commit()
    logger.info(f"Story: {story.title} was deleted by user {current_user.id}.")
    return Response(status_code= status.HTTP_204_NO_CONTENT)



#######################################################  Delete Page  ##################################################################################################

@router.delete('/{story_id}/{page_number}', status_code=status.HTTP_204_NO_CONTENT)
def delete_page(story_id: int,page_number: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user)):
    
    page_query = db.query(models.Pages).filter(models.Pages.story_id == story_id, models.Pages.page_number == page_number)
    page = page_query.first()


    if page == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Page with the id: {page_number} was not found.')

    page_query.delete()
    db.commit()
    logger.info(f"Page number {page_number} of Story id: {story_id} was deleted by {current_user.id}")
    return Response(status_code= status.HTTP_204_NO_CONTENT)



##################################################  Edit/Update Story  ##################################################################################################

@router.put("/{story_id}")
def update_story(story_id: int, updated_story: schemas.CreateStory , db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user) ):

    story_query = db.query(models.Story).filter(models.Story.story_id == story_id)
    story = story_query.first()

    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Story with the id: {story_id} was not found.')

    story_query.update(updated_story.dict(), synchronize_session=False)
    db.commit()

    logger.info(f"Story: {story.title} was updated by {current_user.id}")

    return {"detail": "Story has been updated."}


##################################################  Edit/Update Page  ##################################################################################################

@router.put("/{story_id}/{page_number}")
def update_page(story_id: int, page_number: int, updated_page: schemas.CreatePage, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.admin_user)):
    
    page_query = db.query(models.Pages).filter(models.Pages.story_id == story_id, models.Pages.page_number == page_number)
    page = page_query.first()

    if page == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Page with the id: {page_number} was not found.')
    
    page_query.update(updated_page.dict(), synchronize_session=False)
    db.commit()
    
    logger.info(f"Page number: {page_number} of Story: {story_id} was updated by {current_user.id}")

    return {"detail": "Page has been updated"}
