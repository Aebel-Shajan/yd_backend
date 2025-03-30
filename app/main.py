import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config import Config
from app.auth.routes import router as auth_router
from app.drive.routes import router as drive_router
from app.data_sources.strong.routes import router as strong_router




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

app.include_router(auth_router, prefix="/auth")
app.include_router(drive_router, prefix="/drive")
app.include_router(strong_router, prefix="/data-sources/strong")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)