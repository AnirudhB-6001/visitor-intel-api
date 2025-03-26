from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.airtable import log_to_airtable
from app.ipinfo import enrich_ip_data

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

    # Combine all data to send to Airtable
    payload = {**visit.dict(), **enriched}
    print("Final payload sent to Airtable:", payload)

    # Send to Airtable
    response = log_to_airtable(payload)
    print("Airtable response:", response)

    return {"status": "success", "airtable_id": response.get("id")}