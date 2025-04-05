from fastapi import APIRouter, Depends, HTTPException
from httplib2 import Credentials
import pandas as pd

from app.auth.services import get_current_user_credentials
from app.drive.services import get_data_from_csv, get_data_from_sheet, query_or_create_nested_folder


router = APIRouter(prefix="/fitbit")


@router.get("/calories/{year}")
async def get_fitbit_calories_data(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    outputs_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    data, metadata = get_data_from_sheet(
        credentials=credentials,
        worksheet_name="fitbit_calories",
        file_name="year_in_data",
        parent_id=outputs_folder_id,
        year=year
    )
    
    if data:
        return {
            "status": "success",
            "data": data,
            "metadata": metadata
        }
    


    raise HTTPException(400, detail="Data file for data source not found!")


@router.get("/steps/{year}")
async def get_fitbit_steps_data(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    outputs_folder_id = query_or_create_nested_folder(credentials, "year-in-data")
    data, metadata = get_data_from_sheet(
        credentials=credentials,
        worksheet_name="fitbit_steps",
        file_name="year_in_data",
        parent_id=outputs_folder_id,
        year=year,
    )
    
    if data:
        return {
            "status": "success",
            "data": data,
            "metadata": metadata
        }
    


    raise HTTPException(400, detail="Data file for data source not found!")


@router.get("/sleep/{year}")
async def get_fitbit_sleep_data(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    outputs_folder_id = query_or_create_nested_folder(credentials, "year-in-data")
    
    data, metadata = get_data_from_sheet(
        credentials=credentials,
        worksheet_name="fitbit_sleep",
        file_name="year_in_data",
        parent_id=outputs_folder_id,
        year=year
    )
    
    if data:
        return {
            "status": "success",
            "data": data,
            "metadata": metadata
        }
    


    raise HTTPException(400, detail="Data file for data source not found!")


@router.get("/exercises/{year}")
async def get_fitbit_exercises_data(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    outputs_folder_id = query_or_create_nested_folder(credentials, "year-in-data")
    data, metadata = get_data_from_sheet(
        credentials=credentials,
        worksheet_name="fitbit_exercises",
        file_name="year_in_data",
        parent_id=outputs_folder_id,
        year=year
    )
    
    if data:
        return {
            "status": "success",
            "data": data,
            "metadata": metadata
        }
    

    raise HTTPException(400, detail="Data file for data source not found!")
