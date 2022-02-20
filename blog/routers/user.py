from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, models
from sqlalchemy.orm import Session
from ..database import get_db
from ..hashing import Hash

router = APIRouter()


@router.post("/user", response_model=schemas.ShowUser, tags=['users'])
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    new_user = models.User(name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/user/{user_id}', response_model=schemas.ShowUser, tags=['users'])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} is not available")

    return user

