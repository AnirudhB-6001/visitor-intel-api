from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.db import get_db, init_db
from app.ipinfo import enrich_ip_data
from app.models import VisitorLog, VisitorEventLog
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

        print("✅ Record inserted into SQLite:", record.id)
        return {"status": "success", "db_id": record.id}

    except ValidationError as e:
        print("❌ Validation Error:", e)
        return {"status": "error", "reason": "ValidationError", "detail": e.errors()}

    except Exception as ex:
        print("❌ Unexpected error:", ex)
        return {"status": "error", "reason": "InternalServerError"}

# Event logging remains unchanged
class EventLog(BaseModel):
    session_id: str
    fingerprint_id: str
    event_type: str
    event_data: str = None

@app.post("/log-event")
def log_event(event: EventLog, db: Session = Depends(get_db)):
    print("📍 Event received:", event.dict())

    record = VisitorEventLog(
        session_id=event.session_id,
        fingerprint_id=event.fingerprint_id,
        event_type=event.event_type,
        event_data=event.event_data,
        timestamp=datetime.utcnow()
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    print("✅ Event inserted into DB:", record.id)
    return {"status": "event-logged", "event_id": record.id}