from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return {"message": "Hello World"}


@app.get('/blog/unpublished')
def unpublished():
    return {"data": "Imagine an unpublished blogs list here"}


@app.get('/blog/{blog_id}')
def blog_post(blog_id: int):
    return {"data": blog_id}
