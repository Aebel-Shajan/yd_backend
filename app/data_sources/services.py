import math
from typing import Optional
import zipfile
from sqlalchemy import and_, extract, insert, inspect, null, select
from sqlalchemy.orm import Session
import pandas as pd

from app.data_sources.strong.models import StrongWorkout

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
    
    
def get_data_from_table(
    model: StrongWorkout,
    db: Session,
    year: Optional[int]=None
) -> list[dict]:
    data = db.query(model)
    if year:
        data = db.query(model).filter(extract("year", getattr(model, "date")) == year)
    data = data.all()
    # Creating a list of dictionaries with column name, type, and comment
    metadata = [
        {
            "name": column.name,
            "type": str(column.type),  # str() is used to convert type to string representation
            "comment": column.comment
        }
        for column in model.__table__.columns 
    ]
    return data, metadata
    
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


def is_duplicate(
    model,
    data: dict,
    db: Session
) -> bool:
    """
    Check if a given data entry already exists in the database.

    Args:
        session (Session): The SQLModel database session.
        model (SQLModel): The SQLModel table class to check against.
        data (dict): A dictionary representing the new data row.

    Returns:
        bool: True if a duplicate exists, False otherwise.
    """
    # Build the filter dynamically using all non-primary key columns
    filters = []
    for key, value in data.items():
        column = getattr(model, key)
        if is_value_null(value):
            filters.append(column.is_(null()))  # Handle NULL values properly
        else:
            filters.append(column == value)
        

    if not filters:
        return False  # No valid filters, cannot check duplicates

    # Run the query to check for existing duplicates
    statement = select(model).where(and_(*filters))
    result = db.execute(statement).first() is not None
    return result


def is_value_null(value: any) -> bool:
    if type(value) in {float, int}:
        return math.isnan(value)
    elif type(value) == str:
        return value == "" 
    else:
        return value is None