from typing import BinaryIO

from sqlmodel import Session
from app.database import  engine
from app.models import WorkoutActivity
from app.services.utils import  is_duplicate
from yd_extractor.strong import process_workouts

def create_workout(data: WorkoutActivity):
    with Session(engine) as db:
        if is_duplicate(db, WorkoutActivity, data):
            raise ValueError("Workout already exists in table!")
        db.add(data)
        db.commit()
        db.refresh(data)
    return data
    
    
def read_in_csv(csv_file: BinaryIO):
    df = process_workouts(csv_file)
    df = df.fillna(value=0)
    duplicate_rows = 0
    rows = df.shape[0]
    for index, row in df.iterrows():
        new_workout = WorkoutActivity(**row.to_dict())
        try:
            create_workout(new_workout)
        except ValueError:
            duplicate_rows += 1
    return {"message": f"Added {rows - duplicate_rows} rows, found {duplicate_rows} duplicate rows"}
        