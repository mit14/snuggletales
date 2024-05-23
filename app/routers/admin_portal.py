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
def create_story(story: schemas.CreateStory, db: Session = Depends(database.get_db),  ):

    pass