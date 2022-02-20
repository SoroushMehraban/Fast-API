from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from .. import models, schemas


def get_all(db: Session):
    blogs = db.query(models.Blog).all()
    return blogs


def create(db: Session, request: schemas.Blog, current_user):
    new_blog = models.Blog(title=request.title, body=request.body, user_id=current_user.id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


def destroy(blog_id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")
    blog.delete(synchronize_session=False)
    db.commit()

    return {"message": "done"}


def update(blog_id: int, request: schemas.BlogBase, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")

    blog.update(request.dict())
    db.commit()
    return {"message": "Updated successfully"}


def get_blog(blog_id: int, response: Response, db: Session):
    blog = db.query(models.Blog).get(blog_id)
    if blog is None:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"detail": f"Blog with id {blog_id} is not available"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} is not available")
    return blog
