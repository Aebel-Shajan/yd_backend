import os
import pathlib
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from google.oauth2.credentials import Credentials
from app.auth.services import get_current_user_credentials
from app.config import Config
from app.data_sources.amazon.kindle.models import KindleReading
from app.data_sources.services import check_folder_exists_in_zip, upload_df_to_table
from app.database.session import SessionLocal
from app.drive.services import get_data_from_sheet, query_or_create_nested_folder
from yd_extractor import kindle


router = APIRouter(prefix="/kindle")



@router.post("/upload-data")
async def upload_kindle_zip_file(file: UploadFile):
    
    # Validate that uploaded file is a zip
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=406,
            detail="Uploaded file must be a zip!"
        )
    
    # Save file temporarily to file system
    zip_file_path = pathlib.Path(Config.UPLOAD_FOLDER) / file.filename
    with zip_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    uploaded_sources = []
    
    
    # Validate zip file contains specific folder/file
    kindle_folder = (
        "Kindle.ReadingInsights"
        "/datasets"
        "/Kindle.reading-insights-sessions_with_adjustments"
    )
    if check_folder_exists_in_zip(zip_file_path, kindle_folder):
        extracted_data = []
        
        # Reading
        df = kindle.process_reading(
            inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
            zip_path=zip_file_path
        )
        with SessionLocal() as db:
            added_rows, duplicate_rows = upload_df_to_table(
                df,
                model=KindleReading,
                db=db
            )
            extracted_data.append({
                "table_name": "kindle_reading",
                "message": (
                    f"Successfully added {added_rows} rows. "
                    f"Found {duplicate_rows} duplicate rows."
                )
            })
        
        source_info = {
            "source": "kindle",
            "extracted_data": extracted_data
        }
        uploaded_sources.append(source_info)
    
    # Remove temporarily saved file
    os.remove(zip_file_path)
    return {
        "status": "success",
        "message": "Successfully uploaded and processed kindle data.",
        "data":  uploaded_sources
    }

@router.get("/reading/{year}")
async def get_kindle_reading(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
            
    data, metadata =get_data_from_sheet(
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
        
