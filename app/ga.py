import os
import json
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

# Load GA4 credentials from Render environment
credentials_json = os.getenv("GA4_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("GA4_CREDENTIALS_JSON is missing.")

credentials_dict = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# GA4 Property ID
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")
if not GA4_PROPERTY_ID:
    raise ValueError("GA4_PROPERTY_ID is missing.")

# Client
client = BetaAnalyticsDataClient(credentials=credentials)

def fetch_ga_sessions(start_days_ago=7, end_days_ago=0, limit=10):
    print("GA4 Property ID:", GA4_PROPERTY_ID)

    # Convert numeric days ago to GA4-compatible date strings
    start = f"{start_days_ago}daysAgo"
    end = f"{end_days_ago}daysAgo" if end_days_ago > 0 else "today"

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="dateHourMinute"),
            Dimension(name="pagePath"),
            Dimension(name="deviceCategory"),
            Dimension(name="city"),
            Dimension(name="country")
        ],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        limit=limit
    )

    response = client.run_report(request)

    if not response.rows:
        print("No data returned from GA4 API.")

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

    print("Sessions fetched:", session_data)
    return session_data