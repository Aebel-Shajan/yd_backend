from sqlalchemy import Column, Integer, String, Date
from app.models.base import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    exercise = Column(String, nullable=False)