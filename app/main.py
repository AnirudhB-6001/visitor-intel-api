from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.airtable import log_to_airtable
from app.ipinfo import enrich_ip_data
from app.ga import fetch_ga_sessions  # ✅ Moved this to top-level

app = FastAPI()

# Enable CORS so your React frontend can make POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anirudhbatraofficial.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Define the request schema from the frontend
class VisitLog(BaseModel):
    page: str
    referrer: str
    device: str
    session_id: str = None  # Optional field to identify repeat visits

# Main visitor logging endpoint
@app.post("/log-visit")
async def log_visitor(visit: VisitLog, request: Request):
    print("Raw data from frontend:", visit.dict())

    # Extract IP address from request
    ip = request.client.host
    print("Client IP address:", ip)

    # Enrich IP data using IPinfo
    enriched = enrich_ip_data(ip)
    print("Enriched IP data:", enriched)

    # Map data fields to Airtable columns
    payload = {
        "Page Visited": visit.page,
        "Referrer": visit.referrer,
        "Device Type": visit.device,
        "Session ID": visit.session_id,
        "IP Address": ip,
        "City": enriched.get("City"),
        "Region": enriched.get("Region"),
        "Country": enriched.get("Country"),
        "Organization": enriched.get("Organization"),
        "Enriched Source": "IPinfo"
    }

    print("Final payload sent to Airtable:", payload)

    # Send to Airtable
    response = log_to_airtable(payload)
    print("Airtable response:", response)

    return {"status": "success", "airtable_id": response.get("id")}

# GA4 testing route
@app.get("/fetch-ga-data")
async def test_ga():
    sessions = fetch_ga_sessions(start_days_ago=7, end_days_ago=0, limit=10)
    return {"sessions": sessions}
