from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
=======
from starlette.middleware.sessions import SessionMiddleware  # Import the SessionMiddleware
>>>>>>> google-apple_login

from .utils import limiter, setup_exception_handlers, setup_logger
from .database import Base, engine
from app.routers import auth, admin_portal, stories, like_story, update_profile, history
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
app.include_router(history.router)

app.mount("/static", StaticFiles(directory="app/website"), name="static")

@app.get("/")
def root():
    logger.info("Root endpoint was accessed")
<<<<<<< HEAD
    # Directly return the index.html file
    return FileResponse("app/website/index.html")
=======
    return {"message": "Hello World"}
>>>>>>> google-apple_login
