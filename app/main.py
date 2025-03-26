from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.airtable import log_to_airtable
from app.ipinfo import enrich_ip_data

app = FastAPI()

# ✅ Enable CORS so your React frontend can make POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anirudhbatraofficial.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# ✅ Define the request schema from the frontend
class VisitLog(BaseModel):
    page: str
    referrer: str
    device: str

# ✅ Main visitor logging endpoint
@app.post("/log-visit")
async def log_visitor(visit: VisitLog, request: Request):
    print("Raw data from frontend:", visit.dict())

    # ✅ Extract IP address from the incoming request (for deployed version)
    ip = request.client.host
    print("Client IP address:", ip)

    # ✅ Enrich IP address using IPinfo
    enriched = enrich_ip_data(ip)
    print("Enriched IP data:", enriched)

    # ✅ Combine frontend data + enriched data
    payload = {**visit.dict(), **enriched}
    print("Final payload sent to Airtable:", payload)

    # ✅ Send to Airtable
    response = log_to_airtable(payload)
    print("Airtable response:", response)

    return {"status": "success", "airtable_id": response.get("id")}