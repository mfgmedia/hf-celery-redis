from fastapi import FastAPI
from app.api import router

app = FastAPI(title="FastAPI Celery Image Processor")

# Include API routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "FastAPI is running with Celery and Redis!"}
