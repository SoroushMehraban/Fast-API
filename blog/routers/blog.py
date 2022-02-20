from fastapi import APIRouter, Depends, status, HTTPException, Response
from .. import schemas, database, models
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..repository import blog

router = APIRouter(
    prefix='/blog',
    tags=['Blogs']
)


@router.get('/', response_model=List[schemas.ShowBlog])
def all_blogs(db: Session = Depends(get_db)):
    return blog.get_all(db)


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(request: schemas.BlogBase, db: Session = Depends(get_db)):
    return blog.create(db, request)


@router.delete('/{blog_id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(blog_id, db: Session = Depends(get_db)):
    return blog.destroy(blog_id, db)


@router.put('/{blog_id}', status_code=status.HTTP_202_ACCEPTED)
def update(blog_id, request: schemas.BlogBase, db: Session = Depends(get_db)):
    return blog.update(blog_id, request, db)


@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.ShowBlog)
def get_blog(blog_id, response: Response, db: Session = Depends(get_db)):
    return blog.get_blog(blog_id, response, db)
