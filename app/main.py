from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.airtable import log_to_airtable
from app.ipinfo import enrich_ip_data

app = FastAPI()

# ✅ Enable CORS so your React site can POST to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anirudhbatraofficial.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Request schema
class VisitLog(BaseModel):
    page: str
    referrer: str
    device: str

@app.post("/log-visit")
async def log_visitor(visit: VisitLog):
    print("Raw data from frontend:", visit.dict())

    # Use dummy IP for local testing. For live version, replace with request.client.host
    ip = "8.8.8.8"
    print("Client IP address:", ip)

    enriched = enrich_ip_data(ip)
    print("Enriched IP data:", enriched)

    payload = {**visit.dict(), **enriched}
    print("Final payload sent to Airtable:", payload)

    response = log_to_airtable(payload)
    print("Airtable response:", response)

    return {"status": "success", "airtable_id": response.get("id")}