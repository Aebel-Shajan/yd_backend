from app.db.database import SessionLocal
from app.models.workout import Workout
from app.schema.workout import WorkoutSchema
from app.services.utils import check_duplicate


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