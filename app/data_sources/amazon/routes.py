from google.oauth2.credentials import Credentials


from fastapi import APIRouter, Depends, UploadFile

from app.auth.services import get_current_user_credentials
from app.data_sources.amazon.kindle.routes import router as kindle_router

router = APIRouter(prefix="/amazon")
router.include_router(kindle_router)
# NOTE: For amazon data, you can request for all data in one zip or 
#   choose to indiviually download data for different apps.

@router.post("/upload-data")
async def upload_amazon_data(
    file: UploadFile,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    # TODO: 
    pass
    