from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware  # Import the SessionMiddleware

from .utils import limiter, setup_exception_handlers, setup_logger
from .database import Base, engine
from app.routers import auth, admin_portal, stories, like_story, update_profile
from .config import settings

app = FastAPI()


app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application state and setup
app.state.limiter = limiter
setup_exception_handlers(app)
logger = setup_logger()

# Include routers from various modules
app.include_router(auth.router)
app.include_router(admin_portal.router)
app.include_router(stories.router)
app.include_router(like_story.router)
app.include_router(update_profile.router)

@app.get("/")
def root():
    logger.info("Root endpoint was accessed")
    return {"message": "Hello World"}
