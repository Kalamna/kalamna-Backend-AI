from fastapi import FastAPI
from fastapi_exception_handlers import add_exception_handlers
from app.core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger("app")


app = FastAPI()
add_exception_handlers(app)


@app.get("/")
def index():
    return {"message": "Hello, World!"}
