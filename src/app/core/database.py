from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from app.core.db_init import create_database_if_not_exists

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/foodflow")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    # Create database if it doesn't exist
    create_database_if_not_exists()
    
    # Create tables
    from app.models.restaurant import Base as RestaurantBase
    from app.models.config import Base as ConfigBase
    from app.models.audit import Base as AuditBase
    RestaurantBase.metadata.create_all(bind=engine)
    ConfigBase.metadata.create_all(bind=engine)
    AuditBase.metadata.create_all(bind=engine)