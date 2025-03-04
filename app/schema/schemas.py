from pydantic import BaseModel, PastDate
from datetime import time


class WorkoutSchema(BaseModel):
    date: PastDate
    workout_name: str
    exercise_name: str
    total_sets: int
    max_weight: float
    total_reps: int
    total_volume: float
    workout_duration_minutes: float
    distance: float

    class Config:
        from_attributes = True
        

class ReadingActivitySchema(BaseModel):
    date: PastDate
    start_time: time
    asin: str
    total_reading_minutes: int
    
    class Config:
        from_attributes = True