import os
import requests

AIRTABLE_BASE_ID = os.getenv("appnka3eCAxf93YoF")
AIRTABLE_TABLE_NAME = "Visitor Logs"
AIRTABLE_TOKEN = os.getenv("patpmXlYdghG9ub2B.5fd8c65c565f1322adc0fb5f13041ffceacab5e2f263df07c7953db6db820403")

def log_to_airtable(data):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": data
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()