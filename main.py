from fastapi import FastAPI
from typing import Optional

app = FastAPI()


@app.get('/blog')
def index(limit: int = 10, published: bool = True, sort: Optional[str] = None):
    if published:
        return {"data": f"{limit} published blogs from db"}
    else:
        return {"data": f"{limit} blogs from db"}


@app.get('/blog/unpublished')
def unpublished():
    return {"data": "Imagine an unpublished blogs list here"}


@app.get('/blog/{blog_id}')
def blog_post(blog_id: int):
    return {"data": blog_id}
