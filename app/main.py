from fastapi import FastAPI

from .database import Base, engine
from app.routers import auth
from .config import settings



Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.include_router(registration.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}