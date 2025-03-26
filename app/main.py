from fastapi import FastAPI, Request
from app.airtable import log_to_airtable
from app.ipinfo import enrich_ip_data

app = FastAPI()

@app.post("/log-visit")
async def log_visitor(request: Request):
    data = await request.json()

    # Extract IP from request
    ip = request.client.host

    # Enrich with IPinfo
    enriched = enrich_ip_data(ip)

    # Combine and send to Airtable
    payload = {**data, **enriched}
    response = log_to_airtable(payload)

    return {"status": "success", "airtable_id": response.get("id")}