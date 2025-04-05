from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./year_in_data.db"  # Replace with your DB connection string

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite-specific
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
