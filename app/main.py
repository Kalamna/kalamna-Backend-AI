from fastapi import FastAPI
from app.core.config import setup_logging
import logging

setup_logging()
logger = logging.getLogger("app")

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello, World!"}
