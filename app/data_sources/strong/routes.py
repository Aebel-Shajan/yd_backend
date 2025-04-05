from datetime import datetime
import time
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from google.oauth2.credentials import Credentials
import pandas as pd
from app.auth.services import get_current_user_credentials
from app.drive.services import (
    create_or_update_sheet,
    get_data_from_csv,
    get_records_from_sheet,
    query_or_create_nested_folder,
    upload_or_overwrite,
    download_file,
    query_drive_file
)
from yd_extractor import strong
from app.config import Config
import os

router = APIRouter(prefix="/strong")


@router.post("/upload-data")
async def upload_strong_data(
    file: UploadFile,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    # save_path = Config.UPLOAD_FOLDER + "strong_workouts.csv"
    with file.file as csv_file:
        df = strong.process_workouts(csv_file)
        create_or_update_sheet(
            credentials=credentials,
            df = df,
            worksheet_name="strong_workouts",
            file_name="year_in_data",
            parent_id=output_folder_id
        )
    # os.remove(save_path)
    
    return {
        "status": "success",
        "message": "Successfully uploaded and processed strong data."
    }

    
@router.get("/workouts/{year}")
async def get_strong_workouts(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
            
    data, metadata =get_records_from_sheet(
        credentials,
        worksheet_name="strong_workouts",
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
        