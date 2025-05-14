from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from datetime import datetime
from app.db import get_db, init_db
from app.ipinfo import enrich_ip_data
from app.models import VisitorLog, VisitorEventLog, VisitorDerivedLog
from app import dashboard
from app.intel import get_probable_alias  # 🔍 Intelligent matching layer

app = FastAPI()
app.include_router(dashboard.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://anirudhbatraofficial.com",
        "http://localhost:5173"
    ],
    allow_credentials=True,
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
    entropy_data: dict | None = None
    client_timestamp: str | None = None

@app.post("/log-visit")
async def log_visitor(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        print("🧾 Incoming JSON body:", body)

        visit = VisitLog(**body)
        ip = request.client.host
        enriched = enrich_ip_data(ip)
        entropy = visit.entropy_data or {}

        try:
            parsed_client_ts = (
                datetime.fromisoformat(visit.client_timestamp.replace("Z", "+00:00"))
                if visit.client_timestamp else None
            )
        except Exception as e:
            print("⚠️ Invalid client timestamp:", e)
            parsed_client_ts = None

        subquery = (
            db.query(VisitorLog.visitor_alias)
            .filter(VisitorLog.fingerprint_id == visit.fingerprint_id)
            .filter(VisitorLog.visitor_alias.isnot(None))
            .order_by(VisitorLog.id.asc())
            .first()
        )
        if subquery:
            visitor_alias = subquery[0]
        else:
            count = db.query(VisitorLog.visitor_alias).filter(VisitorLog.visitor_alias.isnot(None)).distinct().count()
            visitor_alias = f"Visitor_{str(count + 1).zfill(3)}"

        subquery = (
            db.query(VisitorLog.session_label)
            .filter(VisitorLog.session_id == visit.session_id)
            .filter(VisitorLog.session_label.isnot(None))
            .order_by(VisitorLog.id.asc())
            .first()
        )
        if subquery:
            session_label = subquery[0]
        else:
            count = db.query(VisitorLog.session_label).filter(VisitorLog.session_label.isnot(None)).distinct().count()
            session_label = f"Session_{str(count + 1).zfill(3)}"

        print("🧠 Alias assignment:", visitor_alias, session_label)

        probable_alias = get_probable_alias(entropy, db)

        record = VisitorLog(
            page=visit.page,
            referrer=visit.referrer,
            device=visit.device,
            session_id=visit.session_id,
            fingerprint_id=visit.fingerprint_id,
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
            entropy_data=visit.entropy_data,
            user_agent=entropy.get("userAgent"),
            screen_res=entropy.get("screen"),
            color_depth=entropy.get("colorDepth"),
            timezone=entropy.get("timezone"),
            language=entropy.get("language"),
            platform=entropy.get("platform"),
            device_memory=entropy.get("deviceMemory"),
            cpu_cores=entropy.get("hardwareConcurrency"),
            gpu_vendor=entropy.get("webglVendor"),
            gpu_renderer=entropy.get("webglRenderer"),
            canvas_hash=entropy.get("canvas"),
            audio_hash=entropy.get("audio"),
            visitor_alias=visitor_alias,
            session_label=session_label,
            client_timestamp=parsed_client_ts,
            probable_alias=probable_alias,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        visit_type = "Returning" if subquery else "New"
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

        print("✅ Record inserted into PostgreSQL:", record.id)
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
    entropy_data: dict | None = None
    client_timestamp: str | None = None

@app.post("/log-event")
def log_event(event: EventLog, request: Request, db: Session = Depends(get_db)):
    print("📍 Event received:", event.dict())

    ip = request.client.host
    enriched = enrich_ip_data(ip)
    entropy = event.entropy_data or {}

    try:
        parsed_client_ts = (
            datetime.fromisoformat(event.client_timestamp.replace("Z", "+00:00"))
            if event.client_timestamp else None
        )
    except Exception as e:
        print("⚠️ Invalid client timestamp on event:", e)
        parsed_client_ts = None

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
        entropy_data=event.entropy_data,
        user_agent=entropy.get("userAgent"),
        screen_res=entropy.get("screen"),
        color_depth=entropy.get("colorDepth"),
        timezone=entropy.get("timezone"),
        language=entropy.get("language"),
        platform=entropy.get("platform"),
        device_memory=entropy.get("deviceMemory"),
        cpu_cores=entropy.get("hardwareConcurrency"),
        gpu_vendor=entropy.get("webglVendor"),
        gpu_renderer=entropy.get("webglRenderer"),
        canvas_hash=entropy.get("canvas"),
        audio_hash=entropy.get("audio"),
        timestamp=datetime.utcnow(),
        client_timestamp=parsed_client_ts,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    print("✅ Event inserted into DB:", record.id)
    return {"status": "event-logged", "event_id": record.id}