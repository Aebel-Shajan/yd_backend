
from sqlmodel import SQLModel, Session, select, and_, null
from app.database import engine
import numpy as np

from app.models import WorkoutActivity


from sqlmodel import select, SQLModel, Session
from sqlalchemy import and_

def is_duplicate(session: Session, model: type[SQLModel], data: SQLModel) -> bool:
    """
    Check if a given data entry already exists in the database.

    Args:
        session (Session): The SQLModel database session.
        model (SQLModel): The SQLModel table class to check against.
        data (dict): A dictionary representing the new data row.

    Returns:
        bool: True if a duplicate exists, False otherwise.
    """
    data = data.model_dump()
    # Get all columns excluding the primary key
    columns = [col.name for col in model.__table__.columns if not col.primary_key]

    # Build the filter dynamically using all non-primary key columns
    filters = [getattr(model, col) == data[col] for col in columns if col in data]

    if not filters:
        return False  # No valid filters, cannot check duplicates

    # Run the query to check for existing duplicates
    statement = select(model).where(and_(*filters))
    return session.exec(statement).first() is not None
