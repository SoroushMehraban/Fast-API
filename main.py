from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return {"message": "Hello World"}


@app.get('/about')
def about():
    return {"data": "about page"}
