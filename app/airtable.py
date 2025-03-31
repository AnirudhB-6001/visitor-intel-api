import os
import requests

# === Visitor Logs (Passive) ===
AIRTABLE_PASSIVE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_PASSIVE_TABLE_NAME = "Visitors Log"

# === GA4 Sessions (Raw GA4 Data) ===
AIRTABLE_GA_BASE_ID = os.getenv("AIRTABLE_GA_BASE_ID")
AIRTABLE_GA_TABLE_NAME = "Sessions"

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
DEBUG = True

def log_to_airtable(data):
    url = f"https://api.airtable.com/v0/{AIRTABLE_PASSIVE_BASE_ID}/{AIRTABLE_PASSIVE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"fields": data}

    if DEBUG:
        print("🔄 Sending to Airtable (Passive Visitor Log):")
        print("🔗 URL:", url)
        print("📦 Payload:", payload)

    response = requests.post(url, json=payload, headers=headers)

    if DEBUG:
        print("📨 Airtable raw response:", response.text)

    return response.json()

def push_ga_sessions_to_airtable(sessions):
    url = f"https://api.airtable.com/v0/{AIRTABLE_GA_BASE_ID}/{AIRTABLE_GA_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    inserted_ids = []
    for session in sessions:
        fields = {
            "Timestamp": session.get("timestamp"),
            "Page": session.get("page"),
            "Device": session.get("device"),
            "City": session.get("city"),
            "Country": session.get("country"),
            "Session Source": session.get("session_source"),  # Can be None
            "Sessions": int(session.get("sessions", 0))
        }

        payload = {"fields": fields}

        if DEBUG:
            print("🌀 Pushing GA session to Airtable:", fields)

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            inserted_ids.append(response.json().get("id"))
        else:
            print("⚠️ Airtable GA insert failed:", response.text)

    return inserted_ids