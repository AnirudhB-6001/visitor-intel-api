from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.db import get_db, init_db
from app.ipinfo import enrich_ip_data
from app.models import VisitorLog, VisitorEventLog, VisitorDerivedLog
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anirudhbatraofficial.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"status": "Visitor Intel API is running"}

class VisitLog(BaseModel):
    page: str
    referrer: str
    device: str
    session_id: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    utm_term: str | None = None
    utm_content: str | None = None
    fingerprint_id: str | None = None

@app.post("/log-visit")
async def log_visitor(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        print("🧾 Incoming JSON body:", body)

        visit = VisitLog(**body)
        ip = request.client.host
        print("🌍 Client IP address:", ip)

        enriched = enrich_ip_data(ip)
        print("🔍 Enriched IP data:", enriched)

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

        # Derived enrichment
        existing = db.query(VisitorLog).filter(VisitorLog.fingerprint_id == visit.fingerprint_id).count()
        visit_type = "Returning" if existing > 1 else "New"

        traffic_type = "Direct"
        if visit.utm_source:
            traffic_type = "Paid"
        elif visit.referrer and visit.referrer != "Direct":
            traffic_type = "Referral"

        entry_page = visit.page
        if visit.session_id:
            earliest = db.query(VisitorLog).filter(VisitorLog.session_id == visit.session_id).order_by(VisitorLog.timestamp.asc()).first()
            if earliest:
                entry_page = earliest.page

        session_entries = db.query(VisitorLog).filter(VisitorLog.session_id == visit.session_id).count()
        bounced = "Yes" if session_entries <= 1 else "No"

        geo_region_type = "Domestic" if enriched.get("Country") == "IN" else "International"

        landing_source = "direct"
        if visit.utm_source:
            landing_source = "utm"
        elif visit.referrer and visit.referrer != "Direct":
            landing_source = "referrer"

        derived = VisitorDerivedLog(
            session_id=visit.session_id,
            fingerprint_id=visit.fingerprint_id,
            visit_type=visit_type,
            traffic_type=traffic_type,
            entry_page=entry_page,
            bounced=bounced,
            geo_region_type=geo_region_type,
            landing_source=landing_source,
        )

        db.add(derived)
        db.commit()

        print("✅ Record inserted into SQLite:", record.id)
        return {"status": "success", "db_id": record.id}

    except ValidationError as e:
        print("❌ Validation Error:", e)
        return {"status": "error", "reason": "ValidationError", "detail": e.errors()}

    except Exception as ex:
        print("❌ Unexpected error:", ex)
        return {"status": "error", "reason": "InternalServerError"}

class EventLog(BaseModel):
    session_id: str
    fingerprint_id: str
    event_type: str
    event_data: str = None
    page: str
    referrer: str
    device: str

@app.post("/log-event")
def log_event(event: EventLog, request: Request, db: Session = Depends(get_db)):
    print("📍 Event received:", event.dict())

    ip = request.client.host
    enriched = enrich_ip_data(ip)

    record = VisitorEventLog(
        session_id=event.session_id,
        fingerprint_id=event.fingerprint_id,
        event_type=event.event_type,
        event_data=event.event_data,
        page=event.page,
        referrer=event.referrer,
        device=event.device,
        ip_address=ip,
        city=enriched.get("City"),
        region=enriched.get("Region"),
        country=enriched.get("Country"),
        organization=enriched.get("Organization"),
        enriched_source="IPinfo",
        timestamp=datetime.utcnow(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    print("✅ Event inserted into DB:", record.id)
    return {"status": "event-logged", "event_id": record.id}