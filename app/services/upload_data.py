import pathlib
from typing import BinaryIO
import zipfile

import pandas as pd
from sqlalchemy import insert, inspect
from app.config import Config
from app.models.kindle import KindleReading
from app.models.fibit import (
    FitbitCalories,
    FitbitExercise,
    FitbitSleep,
    FitbitSteps
)
from app.models.strong import StrongWorkout
from app.services.retrieve_data import is_duplicate
from yd_extractor import kindle, fitbit, strong
from sqlalchemy.orm import Session


def read_kindle_data(
    db: Session,
    zip_file_path: str,
):
    extracted_data = []
    # Validate zip file contains specific folder/file
    kindle_folder = (
        "Kindle.ReadingInsights"
        "/datasets"
        "/Kindle.reading-insights-sessions_with_adjustments"
    )
    if check_folder_exists_in_zip(zip_file_path, kindle_folder):
        
        # Reading
        df = kindle.process_reading(
            inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
            zip_path=zip_file_path
        )
        added_rows, duplicate_rows = upload_df_to_table(
            df,
            model=KindleReading,
            db=db
        )
        extracted_data.append({
            "table_name": "kindle_reading",
            "added_rows": added_rows,
            "duplicate_rows": duplicate_rows,
        })
        
    return {
        "source": "kindle",
        "extracted_data": extracted_data
    }
    

def read_fitbit_data(
    db: Session,
    zip_file_path: str
):
    extracted_data = []
    
    fitbit_folder =  "Takeout/Fitbit/Global Export Data"
    if check_folder_exists_in_zip(zip_file_path, fitbit_folder):
        
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
        
        
    return {
        "source": "fitbit",
        "extracted_data": extracted_data
    }


def read_strong_data(
    db: Session,
    csv_file: BinaryIO
):
    extracted_data = []
    df = strong.process_workouts(csv_file)
    added_rows, duplicate_rows = upload_df_to_table(
        df,
        model=StrongWorkout,
        db=db
    )
    extracted_data.append(
        {
            "table_name": "strong_workouts",
            "added_rows": added_rows,
            "duplicate_rows": duplicate_rows
        }
    )
    return {
        "source": "strong",
        "extracted_data": extracted_data
    }


def upload_df_to_table(
    df: pd.DataFrame,
    model,
    db: Session,
    overwrite: bool = False
)-> tuple[int, int]:
    """
    Uploads a pandas DataFrame to a SQLite table using a SQLAlchemy model.

    Args:
        df (pd.DataFrame): The DataFrame to upload.
        model: The SQLAlchemy model class representing the table.
        db (Session): SQLAlchemy database session.
        overwrite (bool): If True, clears the table before inserting.
    """
    # Ensure all columns exist in the model
    model_columns = {c.key for c in inspect(model).mapper.column_attrs}
    df_columns = set(df.columns)

    if not df_columns.issubset(model_columns):
        missing = df_columns - model_columns
        raise ValueError(f"DataFrame contains invalid columns: {missing}")

    # Optional: clear table
    if overwrite:
        db.query(model).delete()
        db.commit()

    # Convert DataFrame rows to model instances

    records = [
        row for row in df.to_dict(orient="records") 
        if not is_duplicate(model, row, db) 
    ]

    
    # Bulk insert
    if len(records) > 0:
        db.execute(insert(model), records)
    
    db.commit()

    added_rows = len(records)
    duplicate_rows = len(df.index) - len(records)
    return added_rows, duplicate_rows


def check_folder_exists_in_zip(zip_path: str, nested_folder_path: str):
    """
    Checks if a nested folder exists within a zip archive.

    Args:
        zip_path (str): The path to the zip archive.
        nested_folder_path (str): The path to the nested folder within the zip.

    Returns:
        bool: True if the nested folder exists, False otherwise.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Add trailing slash to the nested_folder_path to ensure it's a directory
            nested_folder_path = nested_folder_path.rstrip('/') + '/'

            for file_info in zip_file.namelist():
                if file_info.startswith(nested_folder_path):
                    return True  # Found at least one file or folder within the nested folder
            return False  # No files or folders found with the specified prefix
    except FileNotFoundError:
        return False #Zip file not found
    except zipfile.BadZipFile:
        return False #File is not a zip file or is corrupted
    