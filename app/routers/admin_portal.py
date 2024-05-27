from typing import List
from fastapi import  Response, status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from app import database, utils, schemas, models, oauth2



router = APIRouter(prefix= "/admin/dev/api",
                   tags= ["Create Stories and Pages"] 
                   )




###############################################################  LOGIN  ##################################################################################################



@router.post("/login", response_model= schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Not authorized")
    
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={"user_id":user.id})

    return {"access_token": access_token, "token_type": "bearer"}



########################################################  Create Story  ##################################################################################################


@router.post("/story")
def create_story(story: schemas.CreateStory, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user) ):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    
    new_story = models.Story(**story.model_dump())
    db.add(new_story)
    db.commit()
    db.refresh(new_story)

    return {"detail": "Story added successfully"}



#####################################################  Get All Stories  ##################################################################################################


@router.get("/story", response_model=List[schemas.AdminStroyOut])
def get_all_stories(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    stories = db.query(models.Story).all()

    return stories



#########################################################  Create Page  ##################################################################################################


@router.post("/{story_id}/page")
def create_page(story_id: int, page: schemas.CreatePage, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user) ):

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    story_query = db.query(models.Story).filter(models.Story.story_id == story_id)
    story = story_query.first()

    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Story with the id: {story_id} was not found.')
    
    existing_page = db.query(models.Pages).filter(models.Pages.story_id == story_id, models.Pages.page_number == page.page_number).first()
    
    if existing_page:
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
    return {"detail": "Page added successfully"}


################################################  Get Pages of a Story  ##################################################################################################


@router.get("/{story_id}/page", response_model=List[schemas.AdminPageOut])
def get_pages(story_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    pages = db.query(models.Pages).filter(models.Pages.story_id == story_id).all()

    return pages


#######################################################  Delete Story  ##################################################################################################


@router.delete('/{story_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_story(story_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    story_query = db.query(models.Story).filter(models.Story.story_id == story_id)
    story = story_query.first()


    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Story with the id: {story_id} was not found.')

    story_query.delete()
    db.commit()

    return Response(status_code= status.HTTP_204_NO_CONTENT)




#######################################################  Delete Page  ##################################################################################################


@router.delete('/{story_id}/{page_number}', status_code=status.HTTP_204_NO_CONTENT)
def delete_page(story_id: int,page_number: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    page_query = db.query(models.Pages).filter(models.Pages.story_id == story_id, models.Pages.page_number == page_number)
    page = page_query.first()


    if page == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Page with the id: {page_number} was not found.')

    page_query.delete()
    db.commit()

    return Response(status_code= status.HTTP_204_NO_CONTENT)




##################################################  Edit/Update Story  ##################################################################################################

@router.put("/{story_id}")
def update_story(story_id: int, updated_story: schemas.CreateStory , db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user) ):

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    story_query = db.query(models.Story).filter(models.Story.story_id == story_id)
    story = story_query.first()


    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Story with the id: {story_id} was not found.')

    story_query.update(updated_story.dict(), synchronize_session=False)
    db.commit()

    return {"detail": "Story has been updated."}


##################################################  Edit/Update Story  ##################################################################################################


@router.put("/{story_id}/{page_number}")
def update_page(story_id: int, page_number: int, updated_page: schemas.CreatePage, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    page_query = db.query(models.Pages).filter(models.Pages.story_id == story_id, models.Pages.page_number == page_number)
    page = page_query.first()


    if page == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Page with the id: {page_number} was not found.')
    
    page_query.update(updated_page.dict(), synchronize_session=False)
    db.commit()

    return {"detail": "Page has been updated"}
