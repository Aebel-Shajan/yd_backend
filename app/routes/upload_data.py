


import os
import pathlib
import shutil
from fastapi import APIRouter, HTTPException, UploadFile

from app.config import Config
from app.database.session import SessionLocal
import logging
from app.services.upload_data import (
    read_kindle_data, 
    read_fitbit_data, 
    read_strong_data
)
logger = logging.getLogger()

router = APIRouter(prefix="/upload-data")

@router.post("/strong")
async def upload_strong_file(file: UploadFile):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=406,
            detail="Expected upload file to be a csv!"
        )
    # initalise uploaded_sources
    uploaded_sources = []
        
    try:
        with SessionLocal() as db:
            with file.file as csv_file:
                source_info = read_strong_data(db, csv_file)
                uploaded_sources.append(source_info)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}"
        )

        
    return {
        "status": "success",
        "message": "Successfully uploaded and processed amazon data.",
        "data": uploaded_sources
    }


@router.post("/amazon")
async def upload_amazon_zip_file(file: UploadFile):
    
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
        
    # initalise uploaded_sources
    uploaded_sources = []
        
    try:
        with SessionLocal() as db:
            source_info = read_kindle_data(db, zip_file_path)
            uploaded_sources.append(source_info)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}"
        )
    finally:
        os.remove(zip_file_path)
        
    return {
        "status": "success",
        "message": "Successfully uploaded and processed amazon data.",
        "data": uploaded_sources
    }


@router.post("/google")
async def upload_google_zip_file(file: UploadFile):
    logger.info("Uploading zip file...")
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
        del file
        logger.info("file copied into file system...")
        
    # initalise uploaded_sources
    uploaded_sources = []
        
    try:
        with SessionLocal() as db:
            logger.info("Reading data into db...")
            source_info = read_fitbit_data(db, zip_file_path)
            uploaded_sources.append(source_info)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}"
        )
    finally:
        os.remove(zip_file_path)
        
    return {
        "status": "success",
        "message": "Successfully uploaded and processed amazon data.",
        "data": uploaded_sources
    }

    