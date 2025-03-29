from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import secrets
from app.config import Config
from app.auth.routes import router as auth_router
from app.drive.routes import router as drive_router




app = FastAPI(title="Google OAuth2 Drive API Application")

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)