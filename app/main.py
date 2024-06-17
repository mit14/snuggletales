from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .utils import limiter, setup_exception_handlers, setup_logger
from .database import Base, engine
from app.routers import auth, admin_portal, stories, like_story
from .config import settings





# Base.metadata.create_all(bind=engine) ##// deactivated because using alembic 

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.limiter = limiter
setup_exception_handlers(app)

logger = setup_logger()


# app.include_router(registration.router)
app.include_router(auth.router)
app.include_router(admin_portal.router)
app.include_router(stories.router)
app.include_router(like_story.router)


app.mount("/static", StaticFiles(directory="app/website"), name="static")

@app.get("/")
def root():
    logger.info("Root endpoint was accessed")
    # Directly return the index.html file
    return FileResponse("app/website/index.html")