import os
import pathlib
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from google.oauth2.credentials import Credentials
from app.auth.services import get_current_user_credentials
from app.config import Config
from app.data_sources.services import check_folder_exists_in_zip
from app.drive.services import create_or_update_sheet, get_records_from_sheet, query_or_create_nested_folder
from yd_extractor import kindle


router = APIRouter(prefix="/kindle")



@router.post("/upload-data")
async def upload_kindle_zip_file(
    file: UploadFile,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=406,
            detail="Uploaded file must be a zip!"
        )
    
    
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    zip_file_path = pathlib.Path(Config.UPLOAD_FOLDER) / file.filename
    with zip_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    uploaded_sources = []
    
    kindle_folder = (
        "Kindle.ReadingInsights"
        "/datasets"
        "/Kindle.reading-insights-sessions_with_adjustments"
    )
    if check_folder_exists_in_zip(zip_file_path, kindle_folder):
        uploaded_sources.append("kindle")
        
        # Reading
        df = kindle.process_reading(
            inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
            zip_path=zip_file_path
        )
        create_or_update_sheet(
            credentials=credentials,
            df = df,
            worksheet_name="kindle_reading",
            file_name="year_in_data",
            parent_id=output_folder_id
        )
    
    os.remove(zip_file_path)
    return {
        "status": "success",
        "message": "Successfully uploaded and processed kindle data.",
        "data": {
            "uploaded_sources": uploaded_sources
        }
    }

@router.get("/reading/{year}")
async def get_kindle_reading(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
            
    data, metadata =get_records_from_sheet(
        credentials,
        worksheet_name="kindle_reading",
        file_name="year_in_data",
        parent_id=output_folder_id,
        year=year
    )

    if data:
        return {
            "status": "success",
            "data": data,
            "metadata": metadata
        }
    
    raise HTTPException(400, detail="Data file for strong data source not found!")
        
