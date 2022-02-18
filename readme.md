# FastAPI

My first FastAPI project. It's based on [this tutorial on YouTube](https://www.youtube.com/watch?v=7t2alSnE2-I).

## Install

### FastAPI

`pip install fastapi`

### Uvicorn

It's a web server that runs our API.  
`pip install uvicorn`

## Run the server

After creating the main file, namely `main.py`, the easiest thing to write is:

```
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return {"message": "Hello World"}
```

Then we can run the server using the following command:  
`unicorn main:app --reload`  
In the preceding command, `main` is the name of our file and `app` is the instance we created in the code. In
addition, `--reload` is for automatically reloading after a change in our code.

## Important notes

### Dynamic routing

```
@app.get('/blog/{blog_id}')
def blog_post(blog_id: int):
    return {"data": blog_id}
```

On invalid URL cases, such as `/blog/abcd`, FasAPI automatically generates the following response without any error
handling on our side:  
`{"detail":[{"loc":["path","blog_id"],"msg":"value is not a valid integer","type":"type_error.integer"}]}`

### Function ordering matters

```
@app.get('/blog/{blog_id}')
def blog_post(blog_id: int):
    return {"data": blog_id}


@app.get('/blog/unpublished')
def unpublished():
    return {"data": "Imagine an unpublished blogs list here"}
```

It returns invalid URL as response. Because `blog_post` executes and `blog_id` has to be an integer. Hence, ordering
matters!

### API Docs

#### Swagger UI

`http://localhost:8000/docs`

#### ReDoc

`http://localhost:8000/redoc`

### Query Parameters

```
@app.get('/blog')
def index(limit: int = 10, published: bool = True):
    if published:
        return {"data": f"{limit} published blogs from db"}
    else:
        return {"data": f"{limit} blogs from db"}
```

If default value is not set, then FastAPI assumes that the query parameter is required. In case if it is not required
and is optional, we use `Optional` from `typing`:
```
from typing import Optional

@app.get('/endpoint')
def index(param: Optional[str] = None):
   ...
```
Note that `Optional` is only used by the editor to help us find errors in our code. FastAPI uses `str` part that we pass.

### Request Body (POST request)
```
from pydantic import BaseModel

class Blog(BaseModel):
    title: str
    content: str
    published: Optional[bool]
    
@app.post('/blog')
def create_blog(blog: Blog):
    return {
        'message': "Blog is created",
        'data': {
            'title': blog.title,
            'content': blog.content,
            'published': blog.published
        }
    }
```

### Add database and ORM
First install sqlalchemy:  
`pip install sqlalchemy`

Then open a `database.py` file with the following content:
```
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
```
Then create a `models.py` and a model like the following content:
```
from sqlalchemy import Column, Integer, String
from .database import Base


class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
```
Finally, create all tables (if not exists) in the `main.py`:
```
from fastapi import FastAPI
from . import schemas, models
from .database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
...
```

### Store given data on database
```
from fastapi import FastAPI, Depends
from . import schemas, models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/blog')
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog
```
# Get data from database
```
@app.get('/blog')
def all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/blog/{id}')
def get_blog(blog_id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).get(blog_id)
    return blog
```
