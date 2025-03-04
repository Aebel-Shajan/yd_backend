from sqlalchemy import Column, Integer, String, Date, Float, Time
from app.models.base import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    workout_name = Column(String, nullable=False)
    exercise_name = Column(String, nullable=False)
    total_sets = Column(Integer, nullable=False)
    max_weight= Column(Float, nullable=False)
    total_reps= Column(Integer, nullable=False)
    total_volume = Column(Float, nullable=False)
    workout_duration_minutes= Column(Float, nullable=False)
    distance = Column(Integer, nullable=False)