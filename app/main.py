from fastapi import FastAPI
from app.core.config import setup_logging
import logging


setup_logging()

logger = logging.getLogger("app")


app = FastAPI(
    title="Kalamna Backend API",
    description="Backend API for Kalamna - Customer Service Egyptian AI-powered platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/")
def hello():
    return {"message": "Hello, World!"}
