from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.db import get_db, init_db
from app.ipinfo import enrich_ip_data
from app.models import VisitorLog, VisitorEventLog, VisitorDerivedLog
from app import dashboard
from app.intel import get_probable_alias
from fastapi.responses import JSONResponse

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
    session_id: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    fingerprint_id: Optional[str] = None
    entropy_data: Optional[dict] = None
    client_timestamp: Optional[str] = None

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
        visitor_alias = subquery[0] if subquery else f"Visitor_{str(db.query(VisitorLog.visitor_alias).filter(VisitorLog.visitor_alias.isnot(None)).distinct().count() + 1).zfill(3)}"

        subquery = (
            db.query(VisitorLog.session_label)
            .filter(VisitorLog.session_id == visit.session_id)
            .filter(VisitorLog.session_label.isnot(None))
            .order_by(VisitorLog.id.asc())
            .first()
        )
        session_label = subquery[0] if subquery else f"Session_{str(db.query(VisitorLog.session_label).filter(VisitorLog.session_label.isnot(None)).distinct().count() + 1).zfill(3)}"

        print("🧠 Alias assignment:", visitor_alias, session_label)

        match_result = get_probable_alias(db, entropy, visit.fingerprint_id)
        probable_alias = match_result["probable_alias"]
        probable_score = match_result["probable_score"]
        best_match_alias = match_result["best_match_alias"]
        best_match_score = match_result["best_match_score"]

        if probable_alias:
            print(f"🤖 Probable match detected: {probable_alias} (Score: {probable_score:.2f})")
        else:
            print(f"🔎 No confident match. Best guess: {best_match_alias} (Score: {best_match_score:.2f})")

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
            probable_alias=probable_alias,
            probable_score=probable_score,
            best_match_alias=best_match_alias,
            best_match_score=best_match_score,
            client_timestamp=parsed_client_ts,
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
        landing_source = "utm" if visit.utm_source else ("referrer" if visit.referrer and visit.referrer != "Direct" else "direct")

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
    event_data: Optional[str] = None
    page: str
    referrer: str
    device: str
    entropy_data: Optional[dict] = None
    client_timestamp: Optional[str] = None

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


# ✅ NEW: Exit timestamp logging
class ExitLogRequest(BaseModel):
    session_id: str
    page: str
    exit_time: str  # ISO format expected

@app.post("/log-exit")
def log_exit(data: ExitLogRequest, db: Session = Depends(get_db)):
    try:
        print("📤 Incoming /log-exit payload:", data.dict())
        parsed_exit_ts = datetime.fromisoformat(data.exit_time.replace("Z", "+00:00"))

        log = (
            db.query(VisitorLog)
            .filter(VisitorLog.session_id == data.session_id)
            .filter(VisitorLog.page == data.page)
            .order_by(VisitorLog.timestamp.desc())
            .first()
        )

        if not log:
            raise HTTPException(status_code=404, detail="Matching visit not found")

        client_ts = log.client_timestamp
        if client_ts and client_ts.tzinfo is None:
            client_ts = client_ts.replace(tzinfo=timezone.utc)

        time_on_page = int((parsed_exit_ts - client_ts).total_seconds()) if client_ts else None

        log.page_exit_time = parsed_exit_ts
        log.time_on_page = time_on_page

        print(f"🕒 Calculated time on page: {time_on_page}s | Exit: {parsed_exit_ts} | Entry: {client_ts}")
        db.commit()

        return JSONResponse(content={
            "status": "updated",
            "time_on_page": time_on_page
        })

    except Exception as ex:
        print("❌ Error in /log-exit:", ex)
        return JSONResponse(status_code=500, content={
            "status": "error",
            "reason": str(ex)
        })