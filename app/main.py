from fastapi import FastAPI
from fastapi_exception_handlers import add_exception_handlers

app = FastAPI()
add_exception_handlers(app)


@app.get("/")
def index():
    return {"message": "Hello, World!"}
