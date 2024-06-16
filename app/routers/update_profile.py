from fastapi import  Response, status, HTTPException, Depends, APIRouter
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

@router.delete("/delete_profile", status_code= status.HTTP_204_NO_CONTENT)
def delete_profile(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):

    user_query = db.query(models.User).filter(current_user == models.User.id)
    user = user_query.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User not found.')

    user_query.delete()
    db.commit()

    return Response(status_code= status.HTTP_204_NO_CONTENT)

