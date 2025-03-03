

from sqlalchemy import and_, null
from app.db.database import SessionLocal
import numpy as np


def check_duplicate(model, data: dict) -> bool:
    """Checks if an identical row exists in the given model, handling NULL values.

    Args:
        model (_type_): SQLAlchemy model.
        data (dict): Dictionary of field values to check for duplicates.

    Returns:
        bool: True if duplicate exists, false otherwise.
    """
    with SessionLocal() as db:
        filters = []
        for key, value in data.items():
            column = getattr(model, key)
            if value is None or value =="":
                filters.append(column.is_(null()))  # Handle NULL values properly
            else:
                filters.append(column == value)
        
        query = db.query(model).filter(and_(*filters))
        return db.query(query.exists()).scalar()