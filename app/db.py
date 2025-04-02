import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models import Base

# ✅ Use PostgreSQL if available
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Safety check
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL environment variable not set!")

# ✅ Create PostgreSQL engine
engine = create_engine(DATABASE_URL)

# ✅ Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Init
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created successfully.")