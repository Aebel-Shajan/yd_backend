from app.db.database import SessionLocal
from app.models.workout import Workout


def create_workout(data: dict):
    with SessionLocal() as db:
        new_workout = Workout(
            name=data["name"], 
            exercise=data["exercise"],
            date=data["date"],
        )
        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)

    return {
        "id": new_workout.id, 
        "date": new_workout.date,
        "name": new_workout.name, 
        "exercise": new_workout.exercise
    }