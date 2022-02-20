from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..hashing import Hash


def create_user(request: schemas.User, db: Session):
    new_user = models.User(name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user(user_id: int, db: Session):
    user = db.query(models.User).get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} is not available")

    return user
