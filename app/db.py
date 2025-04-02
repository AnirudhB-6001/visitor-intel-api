import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models import Base
from dotenv import load_dotenv

# ✅ Load .env variables
load_dotenv()

# ✅ Use PostgreSQL URL from env vars
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Use PostgreSQL engine
engine = create_engine(DATABASE_URL)

# ✅ Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === Function to get DB session ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Init DB (create tables) ===
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created successfully.")