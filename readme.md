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
