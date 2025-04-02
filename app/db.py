import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.models import Base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection from .env
POSTGRES_DB_URL = os.getenv("DATABASE_URL")

if not POSTGRES_DB_URL:
    raise RuntimeError("❌ DATABASE_URL is missing in .env file!")

# Create SQLAlchemy engine
engine = create_engine(POSTGRES_DB_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DB Initialization
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL tables created successfully.")
    except OperationalError as e:
        print("❌ Database initialization error:", e)