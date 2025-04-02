import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models import Base

# ✅ Get from Render env vars
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Fail fast if env var is not set
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL environment variable not set.")

# ✅ Use PostgreSQL
engine = create_engine(DATABASE_URL)

# ✅ Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Init DB
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created successfully.")
