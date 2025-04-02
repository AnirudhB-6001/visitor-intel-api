from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from app.models import Base  # Import Base from models.py

# SQLite DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "visitor_logs.db")

# Create the SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === Function to get a DB session ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Function to initialize the DB (creates tables if not exist) ===
def init_db():
    Base.metadata.create_all(bind=engine)