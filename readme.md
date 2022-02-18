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


