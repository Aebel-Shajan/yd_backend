from fastapi import APIRouter
from app.data_sources.google.routes import router as google_router
from app.data_sources.strong.routes import router as strong_router

router = APIRouter(prefix="/data-sources")

router.include_router(google_router)
router.include_router(strong_router)
