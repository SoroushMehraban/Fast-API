from fastapi import APIRouter, Depends, status, HTTPException, Response
from .. import schemas, database, models
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()


@router.get('/blog', response_model=List[schemas.ShowBlog], tags=['blogs'])
def all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@router.post('/blog', status_code=status.HTTP_201_CREATED, tags=['blogs'])
def create(request: schemas.BlogBase, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body, user_id=1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@router.delete('/blog/{blog_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['blogs'])
def destroy(blog_id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")
    blog.delete(synchronize_session=False)
    db.commit()

    return {"message": "done"}


@router.put('/blog/{blog_id}', status_code=status.HTTP_202_ACCEPTED, tags=['blogs'])
def update(blog_id, request: schemas.BlogBase, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")

    blog.update(request.dict())
    db.commit()
    return {"message": "Updated successfully"}


@router.get('/blog/{id}', status_code=status.HTTP_200_OK, response_model=schemas.ShowBlog, tags=['blogs'])
def get_blog(blog_id, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).get(blog_id)
    if blog is None:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"detail": f"Blog with id {blog_id} is not available"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} is not available")
    return blog
