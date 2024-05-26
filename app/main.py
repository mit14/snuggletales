from fastapi import FastAPI

from .database import Base, engine
from app.routers import auth, admin_portal
from .config import settings

from fastapi.middleware.cors import CORSMiddleware



# Base.metadata.create_all(bind=engine) // deactivated because using alembic 

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
app.include_router(admin_portal.router)

@app.get("/")
def root():
    return {"message": "Hello World"}

