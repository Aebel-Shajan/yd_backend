from typing import Optional
from sqlmodel import Field, SQLModel, Time, Date
import datetime
import time



class WorkoutActivity(SQLModel, table=True):
    __tablename__ = "workout_activity"
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime.date 
    workout_name: str
    exercise_name: str
    total_sets: int
    max_weight: float
    total_reps: int
    total_volume: float
    workout_duration_minutes: float
    distance: float
    

class ReadingActivity(SQLModel, table=True):
    __tablename__ = "reading_activity"
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime.date
    start_time: datetime.time
    asin: str
    total_reading_minutes: int
    

    