from typing import Optional
from sqlmodel import Field, SQLModel, Time, Date
import datetime
from pydantic import BaseModel


class TimeSeriesActivity(SQLModel):
    date: datetime.date 
    value: float

class CalorieActivity(TimeSeriesActivity, table=True):
    __tablename__="calorie_activity"
    id: Optional[int] = Field(default=None, primary_key=True)

class StepActivity(TimeSeriesActivity, table=True):
    __tablename__="step_activity"
    id: Optional[int] = Field(default=None, primary_key=True)
    
class SleepActivity(SQLModel, table=True):
    __tablename__="sleep_activity"
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime.time
    end_time: datetime.time
    total_duration_hours: float
    
class ExerciseActivity(SQLModel, table=True):
    __tablename__="exercise_activity"
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime.date
    start_time: datetime.time
    activity_name: str
    average_heart_rate: float
    calories: int
    active_duration: int
    distance: Optional[float] = Field(default=0)
    pace: Optional[float] = Field(default=0)
    
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
    
    
# Pydantic Models

class ValueColMetaData(BaseModel):
    col: str
    units: str
    
class ActivityMetaData(BaseModel):
    date_col: str
    value_cols: list[ValueColMetaData]
    filter_cols: list[str]