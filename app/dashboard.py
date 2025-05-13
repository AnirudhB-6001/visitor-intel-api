# Purpose: Serve raw data from all logs (VisitorLog, VisitorEventLog, VisitorDerivedLog)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from datetime import datetime

from app.db import get_db
from app.models import VisitorLog, VisitorEventLog, VisitorDerivedLog

router = APIRouter()

# ✅ Helper to serialize SQLAlchemy records (including datetime fields like client_timestamp)
def serialize(model):
    return {
        k: (v.isoformat() if isinstance(v, datetime) else v)
        for k, v in vars(model).items()
        if not k.startswith("_") and k != "metadata"
    }

# ✅ Route: All visitor logs (passive logger)
@router.get("/dashboard/visits")
def dashboard_visits(db: Session = Depends(get_db)):
    records = db.query(VisitorLog).order_by(VisitorLog.id.desc()).limit(100).all()
    return JSONResponse([serialize(r) for r in records])

# ✅ Route: All event logs (event logger)
@router.get("/dashboard/events")
def dashboard_events(db: Session = Depends(get_db)):
    records = db.query(VisitorEventLog).order_by(VisitorEventLog.id.desc()).limit(100).all()
    return JSONResponse([serialize(r) for r in records])

# ✅ Route: All derived logs (derived enrichments)
@router.get("/dashboard/derived")
def dashboard_derived(db: Session = Depends(get_db)):
    records = db.query(VisitorDerivedLog).order_by(VisitorDerivedLog.id.desc()).limit(100).all()
    return JSONResponse([serialize(r) for r in records])