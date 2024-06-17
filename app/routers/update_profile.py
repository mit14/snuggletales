from fastapi import  status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import database, schemas, models, oauth2



router = APIRouter(prefix= "/api/dev/v1/profile",
                   tags= ["Update Profile"]
                   )


@router.put("/update", status_code=status.HTTP_200_OK)
def update_profile(data: schemas.ProfileUpdate, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()

    return {"message": "Profile updated successfully"}