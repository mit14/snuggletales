from fastapi import  Request, status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from loguru import logger
from google.oauth2 import id_token
from google.auth.transport import requests

from app import database, utils, schemas, models, oauth2
from app.config import settings
limiter = Limiter(key_func=get_remote_address)

#import required for login via google
oauth = OAuth()

router = APIRouter(prefix= "/api/dev/v1/user",
                   tags= ["Registration and Authentication"]
                   )



##########################################  REGISTRATION  #################################################################################################


@router.post("/register", status_code=status.HTTP_201_CREATED ,response_model=schemas.UserOut)
@limiter.limit(settings.short_limit)
async def create_user(request: Request,user: schemas.UserCreate, background_tasks: BackgroundTasks,db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()



    if db_user:
        if db_user.provider == 'google':
            logger.warning(f"Email already registered via Google. {db_user.id}")
            raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail= "Email Registered via Google, plesae login via Google.")
        
        elif db_user.provider == 'apple':
            logger.warning(f"Email already registered via Apple. {db_user.id}")
            raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail= "Email Registered via Apple, plesae login via Apple.")

        else:
            logger.info(f"Falied to register user, user already registered: {user.email}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")



    hash_password = utils.hash(user.password)
    user.password = hash_password

    # new_user = models.User(**user.model_dump())  /// old method for unpacking the input, new method to diff. admin user 


    new_user = models.User(
        email = user.email,
        password = hash_password,
        age = user.age,
        # role = "user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    otp = utils.store_otp(db, new_user.id)
    background_tasks.add_task(utils.send_email, user.email, "Your OTP Code", f"Your OTP code is {otp}")
    logger.info(f"New user created, user: {new_user.email}")
    return new_user


@router.post("/verify", status_code=status.HTTP_202_ACCEPTED ,response_model= schemas.Token)
def verify_user(otp_validation: schemas.OTPValidation, db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.email == otp_validation.email).first()
    
    if not user:
        logger.warning(f"Falied to verify, user not found: User input: {otp_validation.email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    elif user.is_verified == True:
        logger.info(f"User already verified. User: {otp_validation.email}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= "User already Verified")
    
    
    if utils.validate_otp(db, user.id, otp_validation.otp):
        user.is_verified = True
        db.commit()
        access_token = oauth2.create_access_token(data={"user_id":user.id} )
        utils.delete_otp(user.id, db)
        logger.info(f"User verification success. User: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    
    else:
        logger.warning(f"Invalid or Expired OTP. User: {otp_validation.email}")
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")
    


#########################################  FORGOT PASSWORD  ##################################################################################################


@router.post("/forgot_password_otp", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.short_limit)
def forgot_password_otp(request: Request,password_reset_request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == password_reset_request.email).first()

    if user.provider == 'google':
        logger.warning(f"Email registered via Google, cannot reset password. {user.id}")
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Email Registered via Google, cannot reset password.")
    
    if user.provider == 'apple':
        logger.warning(f"Email registered via Apple, cannot reset password. {user.id}")
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Email Registered via Google, cannot reset password.")

    if not user:
        logger.warning(f"Falied to request reset password OTP, user not found: {password_reset_request.email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = utils.store_otp(db, user.id)
    background_tasks.add_task(utils.send_email, password_reset_request.email, "Your Password Reset OTP", f"Your OTP code is {otp}")
    logger.info(f"OTP successfully sent for user: {password_reset_request.email}")
    return { "detail": "OTP sent to your email"}


@router.post("/reset_password", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.short_limit)
def reset_password(request: Request,password_reset: schemas.PasswordReset, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == password_reset.email).first()

    if not user:
        logger.warning(f"Falied to reset password, user not found: {password_reset.email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    if utils.validate_otp(db, user.id, password_reset.otp):
        hash_password = utils.hash(password_reset.new_password)
        user.password = hash_password
        db.commit()
        utils.delete_otp(user.id, db)
        logger.info(f"Password successfully reset by user: {user.email}")
        return {"detail": "Password changed, please login."}
    else:
        logger.critical(f"Failed update password attempt for user: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")


#########################################  RESET PASSWORD  ##################################################################################################


@router.post("/update_password", status_code=status.HTTP_201_CREATED, response_model= schemas.Token)
@limiter.limit(settings.long_limit)
def update_password(request: Request, password_update: schemas.PasswordUpdate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == password_update.email).first()

    if not user:
        logger.warning(f"Falied to update password, user not found: {password_update.email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    if utils.verify_password(password_update.old_password, user.password):
        hash_password = utils.hash(password_update.new_password)
        user.password = hash_password
        db.commit()

        access_token = oauth2.create_access_token(data={"user_id":user.id})
        logger.info(f"Password successfully updated by user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    
    else:
        logger.critical(f"Failed update password attempt for user: {user.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')


############################################  LOGIN  ##################################################################################################


@router.post("/login", status_code=status.HTTP_202_ACCEPTED, response_model= schemas.Token)
@limiter.limit(settings.long_limit)
def login_user(request: Request, user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        logger.warning(f"Falied login, user not found: {user_credentials.username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    if user.is_verified == False:
        logger.warning(f"Falied login, user not verified: {user_credentials.username}")
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail= "User not verified, please verify.")

    if user.provider == 'google':
        logger.warning(f"Email already registered via Google. {user_credentials.username}")
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail= "Email Registered via Google, plesae login via Google.")
    
    if user.provider == 'apple':
        logger.warning(f"Email already registered via Apple. {user_credentials.username}")
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail= "Email Registered via Apple, plesae login via Apple.")
    
    if not utils.verify_password(user_credentials.password, user.password):
        logger.critical(f"Failed login attemp for user, incorrect password: {user_credentials.username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={"user_id":user.id})
    logger.info(f"Successful login for user: {user_credentials.username}")
    return {"access_token": access_token, "token_type": "bearer"}

################################################### LOGIN WITH GOOGLE  ################################################################################

@router.post("/verify-google-token")
async def verify_google_token(token_data: schemas.GoogleToken, db: Session = Depends(database.get_db)):
    user_info = await verify_token_and_extract_user_info(token_data.token)
    
    if user_info is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user_query = db.query(models.User).filter_by(email=user_info['email'])
    user = user_query.first()

    if user and user.provider != 'google':
        user_query.update(provider='google', synchronize_session=False)
        db.commit()
        return {"access_token": access_token, "token_type": "bearer"}
    
    if not user:
        user = models.User(
            email=user_info['email'],
            provider='google', 
            provider_id=user_info['provider_id'], 
            is_verified=True
            )
        db.add(user)
        db.commit()

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


async def verify_token_and_extract_user_info(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.google_client_id)
        user_info = {
            "email": idinfo['email'],
            "provider_id": idinfo['sub']
        }
        return user_info
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")