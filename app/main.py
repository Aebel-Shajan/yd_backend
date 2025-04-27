import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

import os
import time
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.auth.routes import router as auth_router
from app.drive.routes import router as drive_router
from app.routes.retrieve_data import router as retrieve_data_router
from app.routes.upload_data import router as upload_data_router
from app.database.base import Base
from app.database.session import engine

Base.metadata.create_all(bind=engine)

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
    "http://localhost:4173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # in milliseconds
    formatted_process_time = f"{process_time:.2f}ms"

    logger.info(f"{request.method} {request.url.path} completed in {formatted_process_time}")

    # You can also add the timing info to the response headers (optional)
    response.headers["X-Process-Time"] = formatted_process_time
    return response

app.include_router(auth_router)
app.include_router(drive_router)
app.include_router(retrieve_data_router)
app.include_router(upload_data_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)