from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./year_in_data.db")  # Default to SQLite if not set

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite-specific
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
