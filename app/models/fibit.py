from sqlalchemy import Column, Date, Float, Integer, String, Time
from app.database.base import Base


class FitbitCalories(Base):
    __tablename__ = "fitbit_calories"
    id = Column(Integer, primary_key=True, index=True, comment="primary_key")
    date = Column(Date, nullable=False, comment="date_column")
    value = Column(Float, nullable=False, comment="value_column [calories]")


class FitbitSteps(Base):
    __tablename__ = "fitbit_steps"
    id = Column(Integer, primary_key=True, index=True, comment="primary_key")
    date = Column(Date, nullable=False, comment="date_column")
    value = Column(Float, nullable=False, comment="value_column [steps]")

class FitbitExercise(Base):
    __tablename__ = "fitbit_exercises"
    
    id = Column(Integer, primary_key=True, index=True, comment="primary_key")
    date = Column(Date, nullable=False, comment="date_column")
    activity_name = Column(String, nullable=False, comment="category_column")
    average_heart_rate = Column(Integer, nullable=True, comment="value_column [bpm]")
    calories = Column(Integer, nullable=False, comment="value_column [calories]")
    distance = Column(Integer, nullable=True, comment="value_column [km]")
    active_duration = Column(Integer, nullable=False, comment="value_column [milliseconds]")
    start_time = Column(Time, nullable=False, comment="time_column")
    pace = Column(Float, nullable=True, comment="value_column [seconds per kilometer]")


class FitbitSleep(Base):
    __tablename__ = "fitbit_sleep"
    
    id = Column(Integer, primary_key=True, index=True, comment="primary_key")
    date = Column(Date, nullable=False, comment="date_column")
    start_time = Column(Time, nullable=False, comment="time_column")
    end_time = Column(Time, nullable=False, comment="time_column")
    total_duration_hours = Column(Float, nullable=False, comment="value_column [hours]")

    