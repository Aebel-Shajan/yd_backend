import math
from typing import Optional, TypedDict
from fastapi import HTTPException
from sqlalchemy import and_, extract, func, null, select
from sqlalchemy.orm import Session
from app.models.strong import StrongWorkout
import re


def pascal_to_snake(pascal_str):
    """
    Convert a PascalCase string to snake_case.
    
    Args:
        pascal_str (str): The PascalCase string to convert
        
    Returns:
        str: The converted snake_case string
    
    Examples:
        >>> pascal_to_snake("HelloWorld")
        "hello_world"
        >>> pascal_to_snake("HTTPResponse")
        "http_response"
    """
    if not pascal_str:
        return ""
    
    # Start with the first character in lowercase
    result = pascal_str[0].lower()
    
    # Process the rest of the string
    for char in pascal_str[1:]:
        if char.isupper():
            # Add underscore before uppercase letters
            result += "_" + char.lower()
        else:
            result += char
            
    return result


    
def get_data_from_table(
    model: StrongWorkout,
    db: Session,
    year: Optional[int]=None
) -> tuple[list, list]:
    data = db.query(model)
    if year:
        data = db.query(model).filter(extract("year", getattr(model, "date")) == year)
    data = data.all()
    # Creating a list of dictionaries with column name, type, and comment
    metadata = get_table_metadata(model)
    return data, metadata


class ColumnMetadata(TypedDict):
    name: str
    type: str
    units: str
    classification: str
    
def get_table_metadata(model) -> list[ColumnMetadata]:
    metadata = [
        {
            "name": column.name,
            "type": str(column.type),  # str() is used to convert type to string representation
            "units": extract_units_from_comment(column.comment),
            "classification": extract_classification_from_comment(column.comment)
        }
        for column in model.__table__.columns 
    ]
    return metadata
    

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


def extract_units_from_comment(comment: str) -> str:
    """
    Extract the content inside square brackets from a comment string.

    Args:
        comment (str): The comment string to extract units from.

    Returns:
        str: The content inside square brackets or "".

    Examples:
        >>> extract_units_from_comment("value_column [kg]")
        "kg"
        >>> extract_units_from_comment("No units here")
        ""
    """
    match = re.search(r"\[(.*?)\]", comment)
    if match:
        return match.group(1)
    return ""


def extract_classification_from_comment(comment: str) -> str:
    column_classifications = [
        "value_column",
        "date_column",
        "category_column"
    ]
    
    for classification in column_classifications:
        if classification in comment:
            return classification
    return ""


def get_nth_percentile(model, db: Session, column: str, nth_percentile: int):
    table_column = getattr(model, column)
    total_count = (
        db.query(func.count(table_column))
        .filter(table_column != 0.0)
        .scalar()
    )
    
    # Calculate the index for the nth percentile (position)
    nth_position = int(total_count * nth_percentile / 100)

    # Fetch the value at the nth percentile position
    result = (
        db.query(table_column)
        .filter(table_column != 0.0)
        .order_by(table_column)
        .offset(nth_position - 1)
        .limit(1)
        .scalar()
    )
    return result


def get_range_for_table_column(
    model,
    column: str,
    db: Session
):
    table_metadata = get_table_metadata(model)
    for column_metadata in table_metadata:
        if column_metadata["name"] == column:
            min = get_nth_percentile(model, db, column, 10)
            max = get_nth_percentile(model, db, column, 90)
            return get_nice_range(min, max)
        
    raise HTTPException(
        status_code=400, 
        detail=f"Column provided ({column}) does not exist within table ({model.__tablename__})."
    ) 
    

def get_nice_range(min_val: float, max_val:float) -> list[float]:
    range_diff = max_val - min_val
    magnitude = 10 ** (len(str(int(range_diff))) - 1)
    lower_bound = (min_val // magnitude) * magnitude
    upper_bound = ((max_val // magnitude) + 1) * magnitude
    return [lower_bound, upper_bound]