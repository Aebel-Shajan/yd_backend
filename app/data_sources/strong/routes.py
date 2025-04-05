from fastapi import APIRouter, UploadFile, HTTPException
from app.data_sources.services import get_data_from_table, upload_df_to_table
from app.database.session import SessionLocal
from yd_extractor import strong
from app.data_sources.strong.models import StrongWorkout

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
        