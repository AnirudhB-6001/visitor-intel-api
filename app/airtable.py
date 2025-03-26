import os
import requests

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = "Visitors Log"  # Ensure exact match with Airtable
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")

# Optional debug mode
DEBUG = True


def log_to_airtable(data):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    # Map data to Airtable column names exactly
    mapped_data = {
        "Page Visited": data.get("page"),
        "Referrer": data.get("referrer"),
        "Device Type": data.get("device"),
        "IP Address": data.get("IP Address"),
        "City": data.get("City"),
        "Region": data.get("Region"),
        "Country": data.get("Country"),
        "Organization": data.get("Organization"),
        "Enriched Source": "IPinfo"  # Static for now
    }

    payload = {
        "fields": mapped_data
    }

    if DEBUG:
        print("🔄 Sending to Airtable:")
        print("🔗 URL:", url)
        print("📝 Headers:", headers)
        print("📦 Payload:", payload)

    response = requests.post(url, json=payload, headers=headers)

    if DEBUG:
        print("📨 Airtable raw response:", response.text)

    return response.json()