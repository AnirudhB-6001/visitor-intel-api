import os
import requests

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = "Visitors Log"
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")

DEBUG = True

def log_to_airtable(data):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": data  # Already pre-mapped in main.py
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
