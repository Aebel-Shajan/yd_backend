
from sqlalchemy import Column, Date, Integer, String, Time
from app.database.base import Base


class KindleReading(Base):
    __tablename__ = "kindle_reading"
    
    id = Column(Integer, primary_key=True, index=True, comment="primary_key")
    date = Column(Date, nullable=False, comment="date_column")
    start_time = Column(Time, nullable=False, comment="time_column")
    asin = Column(String, nullable=False, comment="category_column")
    total_reading_minutes = Column(Integer, nullable=False, comment="value_column [minutes]")
    image = Column(String, nullable=True, comment="image_column")
    