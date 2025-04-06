from sqlalchemy import Column, Date, Float, Integer, String
from app.database.base import Base


class StrongWorkout(Base):
    __tablename__="strong_workouts"
    

    id = Column(Integer, primary_key=True, index=True, comment="primary_key")
    date = Column(Date, nullable=False, comment="date_column")
    workout_name = Column(String, nullable=False, comment="category_column")
    exercise_name = Column(String, nullable=False, comment="category_column")
    total_sets = Column(Integer, nullable=False, comment="value_column")
    max_weight= Column(Float, nullable=True, comment="value_column max")
    total_reps= Column(Integer, nullable=False, comment="value_column")
    total_volume = Column(Float, nullable=False, comment="value_column")
    workout_duration_minutes= Column(Integer, nullable=False, comment="value_column max")
    distance = Column(Integer, nullable=False, comment="value_column")
    