from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db, init_db
from app.ipinfo import enrich_ip_data
from app.models import VisitorLog

app = FastAPI()

# Enable CORS so your React frontend can make POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anirudhbatraofficial.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Initialize the database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Request schema
class VisitLog(BaseModel):
    page: str
    referrer: str
    device: str
    session_id: str = None
    utm_source: str = None
    utm_medium: str = None
    utm_campaign: str = None
    utm_term: str = None
    utm_content: str = None
    fingerprint_id: str = None

@app.post("/log-visit")
def log_visitor(visit: VisitLog, request: Request, db: Session = Depends(get_db)):
    print("📥 Raw data from frontend:", visit.dict())

    ip = request.client.host
    print("🌍 Client IP address:", ip)

    enriched = enrich_ip_data(ip)
    print("🔍 Enriched IP data:", enriched)

    # Create DB record
    record = VisitorLog(
        page=visit.page,
        referrer=visit.referrer,
        device=visit.device,
        session_id=visit.session_id,
        ip_address=ip,
        city=enriched.get("City"),
        region=enriched.get("Region"),
        country=enriched.get("Country"),
        organization=enriched.get("Organization"),
        enriched_source="IPinfo",
        utm_source=visit.utm_source,
        utm_medium=visit.utm_medium,
        utm_campaign=visit.utm_campaign,
        utm_term=visit.utm_term,
        utm_content=visit.utm_content,
        fingerprint_id=visit.fingerprint_id,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    print("✅ Record inserted into SQLite:", record.id)
    return {"status": "success", "db_id": record.id}