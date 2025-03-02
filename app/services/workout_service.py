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

    return {
        "id": new_workout.id, 
        "date": new_workout.date,
        "name": new_workout.name, 
        "exercise": new_workout.exercise
    }
    
    
def read_in_csv(csv_file: BinaryIO):
    df = process_workouts(csv_file)
    for index, row in df.iterrows():
        dict = {
            "date": row['date'],
            "name": row["workout_name"],
            "exercise": row["exercise_name"]
        }
        new_workout = WorkoutSchema(**dict)
        try:
            create_workout(new_workout)
        except ValueError:
            print("duplicate row: ", str(row) )
        