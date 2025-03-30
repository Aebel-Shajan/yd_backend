import os
import pathlib
import shutil
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from google.oauth2.credentials import Credentials

from app.auth.services import get_current_user_credentials
from app.drive.services import query_or_create_nested_folder, upload_or_overwrite
from app.config import Config
from yd_extractor import fitbit
from app.data_sources.google.fitbit.routes import router as fitbit_router

router = APIRouter(prefix="/google")

router.include_router(fitbit_router)


@router.post("/upload-data")
async def upload_google_takout_data(
    file: UploadFile,
    credentials: Credentials = Depends(get_current_user_credentials),
):
    output_folder_id = query_or_create_nested_folder(credentials, "year-in-data/outputs")
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=406,
            detail="Uploaded file must be a zip!"
        )
    # try:
    file_path = pathlib.Path(Config.UPLOAD_FOLDER) / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    df = fitbit.process_calories(
        inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
        zip_path=file_path
    )
    save_path = pathlib.Path(Config.UPLOAD_FOLDER) / "fitbit_calories.csv"
    df.to_csv(save_path, index=False)
    upload_or_overwrite(
        credentials=credentials, 
        file_path=save_path, 
        file_name="fitbit_calories.csv",
        parent_id=output_folder_id
    )
    os.remove(file_path)
    os.remove(save_path)
    
    return {
        "status": "success",
        "message": "Successfully uploaded and processed fibit data."
    }
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")
