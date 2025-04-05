from sqlalchemy import Column, Date, Float, Integer, String
from app.database import Base


class StrongWorkout(Base):
    __tablename__="strong_workouts"
    

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    workout_name = Column(String, nullable=False)
    exercise_name = Column(String, nullable=False)
    total_sets = Column(Integer, nullable=False)
    max_weight= Column(Float, nullable=True)
    total_reps= Column(Integer, nullable=False)
    total_volume = Column(Float, nullable=False)
    workout_duration_minutes= Column(Integer, nullable=False)
    distance = Column(Integer, nullable=False)
    