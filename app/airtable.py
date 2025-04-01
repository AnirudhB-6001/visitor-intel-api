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
        print("📝 Headers:", headers)
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
        # Handle singleSelect field for 'Device'
        device_raw = session.get("device")
        device_value = {"name": device_raw} if isinstance(device_raw, str) else device_raw

        fields = {
            "Timestamp": session.get("timestamp"),
            "Page": session.get("page"),
            "Device": device_value,
            "City": session.get("city"),
            "Country": session.get("country"),
            "Sessions": int(session.get("sessions", 0))
        }

        # Optional field
        session_source = session.get("session_source")
        if session_source:
            fields["Session Source"] = session_source

        payload = {"fields": fields}

        if DEBUG:
            print("🌀 Pushing GA session to Airtable:", fields)

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            inserted_ids.append(response.json().get("id"))
        else:
            print("⚠️ Airtable GA insert failed:")
            print("   🔴 Status Code:", response.status_code)
            try:
                print("   📩 Response JSON:", response.json())
            except Exception as e:
                print("   ⚠️ Failed to parse JSON response:", str(e))
                print("   📄 Raw Response:", response.text)
            print("   📦 Payload was:", payload)

    return inserted_ids