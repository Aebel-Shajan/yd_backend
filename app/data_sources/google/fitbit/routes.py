

from fastapi import APIRouter, Depends, HTTPException
from httplib2 import Credentials
import pandas as pd

from app.auth.services import get_current_user_credentials
from app.drive.services import download_file, query_drive_file, query_or_create_nested_folder


router = APIRouter(prefix="/fitbit")


@router.get("/calories/{year}")
async def get_calorie_data(
    year: int,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    data_file_id = query_drive_file(
        credentials, 
        name="fitbit_calories.csv", 
        parent_id=output_folder_id
    )
    print(data_file_id)
    if data_file_id:    
        file = download_file(credentials, data_file_id)
        df = pd.read_csv(file)
        # Ensure the date column is in datetime format 
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df[df['date'].dt.year == year]
        # Replace nan values
        df = df.fillna("")
        data  = df.to_dict(orient='records')
        return {
            "status": "success",
            "data": data
        }
    
    raise HTTPException(400, detail="Data file for data source not found!")
    