from fastapi import  status, HTTPException, Depends, APIRouter
from fastapi import BackgroundTasks
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from app import database, utils, schemas, models, oauth2



router = APIRouter(prefix= "/api/dev/v1/user",
                   tags= ["Registration and Authentication"]
                   )



##########################################  REGISTRATION  #################################################################################################


@router.post("/register", status_code=status.HTTP_201_CREATED ,response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, background_tasks: BackgroundTasks,db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if db_user:
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

    return new_user


@router.post("/verify", status_code=status.HTTP_202_ACCEPTED ,response_model= schemas.Token)
def verify_user(otp_validation: schemas.OTPValidation, db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.email == otp_validation.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    elif user.is_verified == True:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= "User already Verified")
    
    
    if utils.validate_otp(db, user.id, otp_validation.otp):
        user.is_verified = True
        db.commit()
        access_token = oauth2.create_access_token(data={"user_id":user.id} )
        utils.delete_otp(user.id, db)
        return {"access_token": access_token, "token_type": "bearer"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")
    


#########################################  FORGOT PASSWORD  ##################################################################################################


@router.post("/forgot_password_otp", status_code=status.HTTP_201_CREATED)
def forgot_password_otp(password_reset_request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == password_reset_request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = utils.store_otp(db, user.id)
    background_tasks.add_task(utils.send_email, password_reset_request.email, "Your Password Reset OTP", f"Your OTP code is {otp}")
    
    return { "detail": "OTP sent to your email"}


@router.post("/reset_password", status_code=status.HTTP_201_CREATED)
def reset_password(password_reset: schemas.PasswordReset, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == password_reset.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if utils.validate_otp(db, user.id, password_reset.otp):
        hash_password = utils.hash(password_reset.new_password)
        user.password = hash_password
        db.commit()
        utils.delete_otp(user.id, db)
        return {"detail": "Password changed, please login."}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")


#########################################  RESET PASSWORD  ##################################################################################################


@router.post("/update_password", status_code=status.HTTP_201_CREATED, response_model= schemas.Token)
def update_password(password_update: schemas.PasswordUpdate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == password_update.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if utils.verify_password(password_update.old_password, user.password):
        hash_password = utils.hash(password_update.new_password)
        user.password = hash_password
        db.commit()

        access_token = oauth2.create_access_token(data={"user_id":user.id})
        return {"access_token": access_token, "token_type": "bearer"}
    
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')


############################################  LOGIN  ##################################################################################################


@router.post("/login", status_code=status.HTTP_202_ACCEPTED, response_model= schemas.Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    if user.is_verified == False:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail= "User not verified, please verify.")

    
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={"user_id":user.id})

    return {"access_token": access_token, "token_type": "bearer"}