import os
import requests

IPINFO_TOKEN = os.getenv("7ead18362b085a")

def enrich_ip_data(ip):
    url = f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "IP Address": ip,
            "City": data.get("city"),
            "Region": data.get("region"),
            "Country": data.get("country"),
            "Organization": data.get("org")
        }
    except Exception:
        return {}