from typing import List
from fastapi import  status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from app import database, utils, schemas, models, oauth2



router = APIRouter(prefix= "/admin/dev/api",
                   tags= ["Create Stories and Pages"]
                   )




############################################  LOGIN  ##################################################################################################



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



############################################  Create Story  ##################################################################################################

@router.post("/story")
def create_story(story: schemas.CreateStory, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user) ):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    
    new_story = models.Story(**story.model_dump())
    db.add(new_story)
    db.commit()
    db.refresh(new_story)

    return {"detail": "Story added successfully"}


############################################  Create Page  ##################################################################################################

@router.post("/{story_id}/page")
def create_page(story_id: int, page: schemas.CreatePage, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user) ):

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    story_query = db.query(models.Story).filter(models.Story.story_id == story_id)
    story = story_query.first()

    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Story with the id: {story_id} was not found.')
    
    new_page = models.Pages(story_id= story_id, **page.model_dump())
    db.add(new_page)
    db.commit()
    db.refresh(new_page)

    return {"detail": "Page added successfully"}


############################################  Get All Stories  ##################################################################################################

@router.get("/story", response_model=List[schemas.AdminStroyOut])
def get_all_stories(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    stories = db.query(models.Story).all()

    return stories

