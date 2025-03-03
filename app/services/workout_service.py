from typing import BinaryIO
from app.db.database import SessionLocal, engine
from app.models.workout import Workout
from app.schema.workout import WorkoutSchema
from app.services.utils import check_duplicate
from yd_extractor.strong import process_workouts

def create_workout(data: WorkoutSchema):
    data_dict =data.model_dump()
    if check_duplicate(Workout, data_dict):
        raise ValueError("Workout already exists in table!")
    with SessionLocal() as db:
        new_workout = Workout(**data_dict)
        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)

    return new_workout
    
    
def read_in_csv(csv_file: BinaryIO):
    df = process_workouts(csv_file)
    df = df.fillna(value=0)
    duplicate_rows = 0
    rows = df.shape[0]
    for index, row in df.iterrows():
        new_workout = WorkoutSchema(**row.to_dict())
        try:
            create_workout(new_workout)
        except ValueError:
            duplicate_rows += 1
    return {"message": f"Added {rows - duplicate_rows} rows, found {duplicate_rows} duplicate rows"}
        