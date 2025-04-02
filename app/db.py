import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models import Base

# Read from .env or environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# PostgreSQL engine
engine = create_engine(DATABASE_URL)

# DB session setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to inject DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if not exist
def init_db():
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL tables created successfully.")