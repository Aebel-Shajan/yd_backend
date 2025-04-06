import os
import pathlib
import shutil
from fastapi import APIRouter, UploadFile, HTTPException

from app.data_sources.services import check_folder_exists_in_zip
from app.config import Config
from yd_extractor import fitbit
from app.data_sources.google.fitbit.routes import router as fitbit_router
from app.database.session import SessionLocal
from app.data_sources.services import upload_df_to_table
from app.data_sources.google.fitbit.models import (
    FitbitCalories, 
    FitbitExercise, 
    FitbitSleep,
    FitbitSteps
)

router = APIRouter(prefix="/google")

router.include_router(fitbit_router)


@router.post("/upload-data")
async def upload_google_takeout_data(file: UploadFile):
    
    # Validate zip
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=406,
            detail="Uploaded file must be a zip!"
        )
        
    # try:
    zip_file_path = pathlib.Path(Config.UPLOAD_FOLDER) / file.filename
    with zip_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    uploaded_sources = []
    
    # Fitbit
    if check_folder_exists_in_zip(zip_file_path, "Takeout/Fitbit/Global Export Data"):
        extracted_data = []
        
        with SessionLocal() as db:
            # Calories
            df = fitbit.process_calories(
                inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
                zip_path=zip_file_path
            )
            added_rows, duplicate_rows = upload_df_to_table(
                df=df,
                model=FitbitCalories,
                db=db
            )
            extracted_data.append(
                {
                    "table_name": "fitbit_calories",
                    "added_rows": added_rows,
                    "duplicate_rows": duplicate_rows
                }
            )
            
            # Sleep
            df = fitbit.process_sleep(
                inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
                zip_path=zip_file_path
            )
            added_rows, duplicate_rows = upload_df_to_table(
                df=df,
                model=FitbitSleep,
                db=db
            )
            extracted_data.append(
                {
                    "table_name": "fitbit_sleep",
                    "added_rows": added_rows,
                    "duplicate_rows": duplicate_rows
                }
            )
            
            # Exercises
            df = fitbit.process_exercise(
                inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
                zip_path=zip_file_path
            )
            added_rows, duplicate_rows = upload_df_to_table(
                df=df,
                model=FitbitExercise,
                db=db
            )
            extracted_data.append(
                {
                    "table_name": "fitbit_exercises",
                    "added_rows": added_rows,
                    "duplicate_rows": duplicate_rows
                }
            )
            
            # Steps
            df = fitbit.process_steps(
                inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
                zip_path=zip_file_path
            )
            added_rows, duplicate_rows = upload_df_to_table(
                df=df,
                model=FitbitSteps,
                db=db
            )
            extracted_data.append(
                {
                    "table_name": "fitbit_steps",
                    "added_rows": added_rows,
                    "duplicate_rows": duplicate_rows
                }
            )
            
            uploaded_sources.append(
                {
                    "source": "fitbit",
                    "extracted_data": extracted_data
                }
            )
    
    # Youtube
    if check_folder_exists_in_zip(zip_file_path, "Takeout/YouTube and YouTube Music/history"):
        uploaded_sources.append(
            {
                "source": "youtube",
                "extracted_data": []
            }
        )
        
    os.remove(zip_file_path)
    
    return {
        "status": "success",
        "message": "Successfully uploaded and processed google takeout data.",
        "data": uploaded_sources
    }
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")
