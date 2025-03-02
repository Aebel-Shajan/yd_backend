

from sqlalchemy import and_
from app.db.database import SessionLocal


def check_duplicate(model, data: dict) -> bool:
    """Checks if an identical row exists in the given model.

    Args:
        model (_type_): SQLAlchemy model.
        data (dict): Dictionary of field values to check for duplicates.

    Returns:
        bool: True if duplicate exists, false otherwise.
    """
    # *[] unpacks list
    with SessionLocal() as db:
        query = db.query(model).filter(
            and_(*[getattr(model, key) == value for key, value in data.items()])
        )
        duplicate_exists = db.query(query.exists()).scalar()
        return duplicate_exists