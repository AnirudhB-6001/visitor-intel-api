import os
import json
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

# Load GA4 credentials from JSON string in environment variable
credentials_json = os.getenv("GA4_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("GA4_CREDENTIALS_JSON is missing in environment variables.")

credentials_dict = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# GA4 Property ID
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")
if not GA4_PROPERTY_ID:
    raise ValueError("GA4_PROPERTY_ID is missing in environment variables.")

# Analytics client
client = BetaAnalyticsDataClient(credentials=credentials)

def fetch_ga_sessions(start_days_ago=1, end_days_ago=0, limit=10):
    print("GA4 Property ID:", GA4_PROPERTY_ID)
    
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="dateHourMinute"),
            Dimension(name="pagePath"),
            Dimension(name="deviceCategory"),
            Dimension(name="city"),
            Dimension(name="country"),
            Dimension(name="source")
        ],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date=f"{start_days_ago}daysAgo", end_date=f"{end_days_ago}daysAgo")],
        limit=limit
    )

    response = client.run_report(request)

    session_data = []
    for row in response.rows:
        session = {
            "timestamp": row.dimension_values[0].value,
            "page": row.dimension_values[1].value,
            "device": row.dimension_values[2].value,
            "city": row.dimension_values[3].value,
            "country": row.dimension_values[4].value,
            "referrer": row.dimension_values[5].value,
            "sessions": row.metric_values[0].value
        }
        session_data.append(session)

    return session_data