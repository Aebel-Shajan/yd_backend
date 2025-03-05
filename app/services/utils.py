
from sqlmodel import SQLModel, Session, select, and_, extract
from app.database import engine
from sqlmodel import select, SQLModel, Session
from sqlalchemy import and_
import pandas as pd

def selct_activities_from_db(model: type[SQLModel], year: int):
    with Session(engine) as session:
        statement = select(model).where(extract('year', getattr(model, "date")) == year)
        results = session.exec(statement)
        return [result.model_dump(mode="json") for result in results]

def add_activities_df_to_db(
    df: pd.DataFrame, 
    model: type[SQLModel],
):
    duplicate_rows = 0
    rows = df.shape[0]
    for index, row in df.iterrows():
        new_workout = model(**row.to_dict())
        try:
            add_activity_to_db(new_workout, model)
        except ValueError:
            duplicate_rows += 1
    return {
        "message": (
            f"Added {rows - duplicate_rows} rows,"
            f" found {duplicate_rows} duplicate rows"
        )
    }

def add_activity_to_db(data: SQLModel, model: type[SQLModel]):
    with Session(engine) as session:
        if is_duplicate(session, model, data):
            raise ValueError("Activity already exists in table!")
        session.add(data)
        session.commit()
        session.refresh(data)
    return data

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
