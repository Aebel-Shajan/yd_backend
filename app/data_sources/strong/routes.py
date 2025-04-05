from datetime import datetime
import time
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from google.oauth2.credentials import Credentials
import pandas as pd
from sqlalchemy import Table
from app.auth.services import get_current_user_credentials
from app.data_sources.services import get_data_from_table, upload_df_to_table
from app.database import SessionLocal
from app.drive.services import (
    create_or_update_sheet,
    get_data_from_csv,
    get_data_from_sheet,
    query_or_create_nested_folder,
    upload_or_overwrite,
    download_file,
    query_drive_file
)
from yd_extractor import strong
from app.config import Config
from app.data_sources.strong.models import StrongWorkout
import os

router = APIRouter(prefix="/strong")


@router.post("/upload-data")
async def upload_strong_data(file: UploadFile):
    with file.file as csv_file:
        df = strong.process_workouts(csv_file)
        with SessionLocal() as db:
            added_rows, duplicate_rows = upload_df_to_table(
                df,
                model=StrongWorkout,
                db=db
            )
            return {
                "status": "success",
                "message": (
                    f"Successfully added {added_rows} rows. "
                    f"Found {duplicate_rows} duplicate rows."
                )
            }


@router.get("/workouts/{year}")
async def get_strong_workouts(year: int):
    with SessionLocal() as db:        
        data, metadata =get_data_from_table(
            model=StrongWorkout,
            db=db,
            year=year
        )
        
        if data:
            return {
                "status": "success",
                "data": data,
                "metadata": metadata
            }
        
    raise HTTPException(400, detail="Data file for strong data source not found!")
        