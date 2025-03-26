from fastapi import FastAPI
from pydantic import BaseModel
from app.airtable import log_to_airtable
from app.ipinfo import enrich_ip_data

app = FastAPI()

# Define request schema
class VisitLog(BaseModel):
    page: str
    referrer: str
    device: str

@app.post("/log-visit")
async def log_visitor(visit: VisitLog):
    print("Raw data from frontend:", visit.dict())

    # Extract IP (use dummy for local test since .client.host is localhost)
    ip = "8.8.8.8"  # Temporarily hardcoded for local testing
    print("Client IP address:", ip)

    enriched = enrich_ip_data(ip)
    print("Enriched IP data:", enriched)

    payload = {**visit.dict(), **enriched}
    print("Final payload sent to Airtable:", payload)

    response = log_to_airtable(payload)
    print("Airtable response:", response)

    return {"status": "success", "airtable_id": response.get("id")}