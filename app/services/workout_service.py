from typing import BinaryIO
from app.models import WorkoutActivity
from app.services.utils import  add_activity_to_db
from yd_extractor.strong import process_workouts

    
def process_strong_csv(csv_file: BinaryIO):
    df = process_workouts(csv_file)
    df = df.fillna(value=0)
    duplicate_rows = 0
    rows = df.shape[0]
    for index, row in df.iterrows():
        new_workout = WorkoutActivity(**row.to_dict())
        try:
            add_activity_to_db(new_workout, WorkoutActivity)
        except ValueError:
            duplicate_rows += 1
    return {
        "message": (
            f"Added {rows - duplicate_rows} rows,"
            f" found {duplicate_rows} duplicate rows"
        )
    }
        