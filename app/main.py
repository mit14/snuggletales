from fastapi import FastAPI

from .database import Base, engine
from app.routers import auth
from .config import settings

from fastapi.middleware.cors import CORSMiddleware



Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# app.include_router(registration.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}