# Use a slim Python base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (needed for asyncpg / psycopg / Postgres drivers, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# 1) Copy only requirements first for better Docker layer caching

COPY requirements.txt requirements-dev.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt -r requirements-dev.txt


# 2) Now copy the rest of the project
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Default command: run FastAPI with Uvicorn
# Remove --reload in production if you want
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
