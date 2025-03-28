import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

# Path to your service account key
KEY_PATH = os.path.join("secrets", "visitor-intel-ga-credentials.json")

# GA4 Property ID from environment
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")

# Setup client
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
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