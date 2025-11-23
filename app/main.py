import fastapi

app = fastapi.FastAPI()


@app.get("/")
def index():
    return {"message": "Hello, World!"}