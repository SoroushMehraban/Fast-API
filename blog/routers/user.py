from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, models
from sqlalchemy.orm import Session
from ..database import get_db
from ..hashing import Hash
from ..repository import user

router = APIRouter(
    prefix='/user',
    tags=['Users']
)


@router.post("/", response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    return user.create_user(request, db)


@router.get('/{user_id}', response_model=schemas.ShowUser)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user.get_user(user_id, db)

