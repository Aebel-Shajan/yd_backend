from fastapi import APIRouter, Depends, UploadFile, HTTPException
from google.oauth2.credentials import Credentials
import pandas as pd
from app.auth.services import get_current_user_credentials
from app.drive.services import (
    query_or_create_nested_folder,
    upload_or_overwrite,
    download_file,
    query_drive_file
)
from yd_extractor import strong
from app.config import Config
import os

router = APIRouter()


@router.post("/upload-data")
async def upload_strong_data(
    file: UploadFile,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    save_path = Config.UPLOAD_FOLDER + "strong.csv"
    with file.file as csv_file:
        df = strong.process_workouts(csv_file)
        df.to_csv(save_path, index=False)
        upload_or_overwrite(
            credentials=credentials, 
            file_path=save_path, 
            file_name="strong.csv",
            parent_id=output_folder_id
        )
    os.remove(save_path)
    
    return {
        "status": "success",
        "message": "Successfully uploaded and processed strong data."
    }
    
    
@router.get("/get-data/{year}")
async def get_strong_data(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    data_file_id = query_drive_file(
        credentials, 
        name="strong.csv", 
        parent_id=output_folder_id
    )
    if data_file_id:    
        file = download_file(credentials, data_file_id)
        df = pd.read_csv(file)
        # Ensure the date column is in datetime format 
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df[df['date'].dt.year == year]
        # Replace nan values
        df = df.fillna("")
        data  = df.to_dict(orient='records')
        print(data)
        return {
            "status": "success",
            "data": data
        }
    
    raise HTTPException(400, detail="Data file for strong data source not found!")
        