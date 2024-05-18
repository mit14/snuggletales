from jose import JWSError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models, config
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oath2_scheme = OAuth2PasswordBearer(tokenUrl='login') # need to pass the url endpoint.

#SECERT key
#Algo 
#Expiration time 

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
ACCESS_TOKEN_EXPIRES_WEEKS = config.settings.access_token_expires_weeks

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() +timedelta(weeks=ACCESS_TOKEN_EXPIRES_WEEKS)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        id: str = str(payload.get('user_id'))

        if id is None:
            raise credential_exception
        token_data = schemas.TokenData(user_id=id)

    except JWSError:
        raise credential_exception
    return token_data


def get_current_user(token: str = Depends(oath2_scheme), db: Session = Depends(database.get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validiate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credential_exception)
    
    user = db.query(models.User).filter(models.User.id == token.user_id).first()
    print(user)
    return user