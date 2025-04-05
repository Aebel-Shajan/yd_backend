import os
import pathlib
import shutil
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from google.oauth2.credentials import Credentials

from app.auth.services import get_current_user_credentials
from app.data_sources.services import check_folder_exists_in_zip
from app.drive.services import create_or_update_sheet, query_or_create_nested_folder, upload_or_overwrite
from app.config import Config
from yd_extractor import fitbit
from app.data_sources.google.fitbit.routes import router as fitbit_router

router = APIRouter(prefix="/google")

router.include_router(fitbit_router)


@router.post("/upload-data")
async def upload_google_takeout_data(
    file: UploadFile,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    
    # Validate zip
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=406,
            detail="Uploaded file must be a zip!"
        )
        
    # try:
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    zip_file_path = pathlib.Path(Config.UPLOAD_FOLDER) / file.filename
    with zip_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    uploaded_sources = []
    
    # Fitbit
    if check_folder_exists_in_zip(zip_file_path, "Takeout/Fitbit/Global Export Data"):
        uploaded_sources.append("fitbit")
        # Calories
        df = fitbit.process_calories(
            inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
            zip_path=zip_file_path
        )
        create_or_update_sheet(
            credentials,
            df=df,
            worksheet_name="fibit_calories",
            file_name="year_in_data",
            parent_id=output_folder_id
        )
        
        # Sleep
        df = fitbit.process_sleep(
            inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
            zip_path=zip_file_path
        )
        create_or_update_sheet(
            credentials,
            df=df,
            worksheet_name="fitbit_sleep",
            file_name="year_in_data",
            parent_id=output_folder_id
        )
        
        # Exercises
        df = fitbit.process_exercise(
            inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
            zip_path=zip_file_path
        )
        create_or_update_sheet(
            credentials,
            df=df,
            worksheet_name="fitbit_exercises",
            file_name="year_in_data",
            parent_id=output_folder_id
        )
        
        # Steps
        df = fitbit.process_steps(
            inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
            zip_path=zip_file_path
        )
        create_or_update_sheet(
            credentials,
            df=df,
            worksheet_name="fitbit_steps",
            file_name="year_in_data",
            parent_id=output_folder_id
        )
        
    
    # Youtube
    if check_folder_exists_in_zip(zip_file_path, "Takeout/YouTube and YouTube Music/history"):
        uploaded_sources.append("youtube")
        
    os.remove(zip_file_path)
    
    return {
        "status": "success",
        "message": "Successfully uploaded and processed google takeout data.",
        "data": {
            "uploaded_sources": uploaded_sources
        }
    }
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")
