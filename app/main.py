import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.auth.routes import router as auth_router
from app.drive.routes import router as drive_router
from app.data_sources.routes import router as data_source_router




app = FastAPI(title="Google OAuth2 Drive API Application")
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Add secure session middleware
app.add_middleware(
    SessionMiddleware, 
    secret_key=Config.SECRET_KEY, 
    # session_cookie=True,
    # max_age=86400,  # 24 hours
    # same_site="lax",
    # https_only=True
)
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(drive_router)
app.include_router(data_source_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)