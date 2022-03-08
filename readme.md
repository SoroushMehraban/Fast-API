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

```python
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

```python
@app.get('/blog/{blog_id}')
def blog_post(blog_id: int):
    return {"data": blog_id}
```

On invalid URL cases, such as `/blog/abcd`, FasAPI automatically generates the following response without any error
handling on our side:  
`{"detail":[{"loc":["path","blog_id"],"msg":"value is not a valid integer","type":"type_error.integer"}]}`

### Function ordering matters

```python
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

```python
@app.get('/blog')
def index(limit: int = 10, published: bool = True):
    if published:
        return {"data": f"{limit} published blogs from db"}
    else:
        return {"data": f"{limit} blogs from db"}
```

If default value is not set, then FastAPI assumes that the query parameter is required. In case if it is not required
and is optional, we use `Optional` from `typing`:

```python
from typing import Optional

@app.get('/endpoint')
def index(param: Optional[str] = None):
   ...
```

Note that `Optional` is only used by the editor to help us find errors in our code. FastAPI uses `str` part that we
pass.

### Request Body (POST request)

```python
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

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
```

Then create a `models.py` and a model like the following content:

```python
from sqlalchemy import Column, Integer, String
from .database import Base


class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
```

Finally, create all tables (if not exists) in the `main.py`:

```python
from fastapi import FastAPI
from . import schemas, models
from .database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
...
```

### Store given data on database

```python
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

### Get data from database

```python
@app.get('/blog')
def all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/blog/{id}')
def get_blog(blog_id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).get(blog_id)
    return blog
```

### Delete data from database

```python
@app.delete('/blog/{blog_id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(blog_id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")
    blog.delete(synchronize_session=False)
    db.commit()

    return {"message": "done"}
```

### Update data

Note that `.update()` method provided by SQLAlchemy is a **bulk operation**. In other words, if we filter, and it
returns two rows of a table with the corresponding query, it updates both of them.

```python
@app.put('/blog/{blog_id}', status_code=status.HTTP_202_ACCEPTED)
def update(blog_id, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")

    blog.update(request.dict())
    db.commit()
    return {"message": "Updated successfully"}
```

### Response Model

In cases when we don't want to respond with all the data of a model, we use response model. To do that, add the
following model on `schemas.py`:

```python
class ShowBlog(BaseModel):
    title: str
    body: str

    class Config:
        orm_mode = True
```

In the preceding code, we are saying that we only want to have title and body in the response.

To use it on a path, we have to add `response_model=` on the decorator:

```python
@app.get('/blog/{id}', status_code=status.HTTP_200_OK, response_model=schemas.ShowBlog)
def get_blog(blog_id, response: Response, db: Session = Depends(get_db)):
  ...
```

In cases when we have multiple instance in the response, we have to define response model like the following code:

```python
from typing import List

@app.get('/blog', response_model=List[schemas.ShowBlog])
def all_blogs(db: Session = Depends(get_db)):
   ...
```

### Hashing password

1. `pip install passlib`
2. `pip install bcrypt`
3. `from passlib.context import CryptContext`
4. `pwd_cxt = CryptContext(schemes=['bcrypt'], deprecated="auto")`
5. `hashed_password = pwd_cxt.hash(request.password)`

### JWT Access Token

1. `pip install python-jose`
2. Create a file for JWToken, namely `token.py`, with the following content:

```python
SECRET_KEY = "<SECRET_KEY_HERE>"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

For the `SECRET_KEY`, you can create it with the following command on the terminal:  
`openssl rand -hex 32`

3. Add these two pydantic models on `schemas.py`:

```python
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
```

4. Add the following function to the `token.py`:

```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict,):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

5. Use the preceding function where you get the user data:

```python
access_token = token.create_access_token(data={"sub": user.email})
return {"access_token": access_token, "token_type": "bearer"}
```

### Route behind authentication

1. create a `ouath2.py` with the following content:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import token, database, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_user(email):
    db = next(database.get_db())
    return db.query(models.User).filter(models.User.email == email).first()


def get_current_user(data: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = token.verify_token(data, credentials_exception)
    user = get_user(token_data.email)
    return user

```

Note that `"login"` is the name of the route that is responsible for logging in. It should have the following format:

```python
@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password")

    access_token = token.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}
```

It is important to set request type to `OAuth2PasswordRequestForm`.

2. As you can see, `.verify_token` on `get_current_user` is needed to be implemented. Hence, add the following function
   in `token.py`:

```python
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
```

### Alembic
This is based on [this video](https://www.youtube.com/watch?v=SdcH6IEi6nE&t) on YouTube.

#### Installation:
```text
pip install alembic
```

#### Initialization
```text
alembic init alembic
```

#### Setup
1. Go to `alembic.ini` and change `sqlalchemy.url` with yours.
2. Go to `alembic/env.py` and change `target_metadata` with `Base.metadata`.
   Note that `Base` should be imported from `models.py` that has the tables not the `database.py`

#### Revision
```text
alembic revision --autogenerate -m "<REVISION MESSAGE>"
```

#### Upgrade
Every version has a format like `b1c089bc3896_first_revision.py`. We can upgrade to a specific version using the
following command:
```text
alembic upgrade b1c0
```
And it automatically detects which version we want. Since it is the only version started with `b1c0`.

Another approach is to upgrade to the last version:
```text
alembic upgrade head
```

#### Downgrade
```text
alembic downgrade <REVISION_NAME>
```

