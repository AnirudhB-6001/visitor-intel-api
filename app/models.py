from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()

class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    client_timestamp = Column(DateTime, nullable=True)

    page = Column(String)
    referrer = Column(String)
    device = Column(String)
    session_id = Column(String)
    fingerprint_id = Column(String)
    ip_address = Column(String)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    organization = Column(String)
    enriched_source = Column(String)

    # UTM fields
    utm_source = Column(String)
    utm_medium = Column(String)
    utm_campaign = Column(String)
    utm_term = Column(String)
    utm_content = Column(String)

    # Fingerprinting (plugin count removed)
    entropy_data = Column(JSONB)
    user_agent = Column(Text)
    screen_res = Column(String)
    color_depth = Column(String)
    timezone = Column(String)
    language = Column(String)
    platform = Column(String)
    device_memory = Column(String)
    cpu_cores = Column(String)
    gpu_vendor = Column(String)
    gpu_renderer = Column(String)
    canvas_hash = Column(String)
    audio_hash = Column(String)

    # ✅ Core identity fields
    visitor_alias = Column(String)
    session_label = Column(String)

    # ✅ Intelligent matching layer
    probable_alias = Column(String)  # This is the fuzzy-matched alias (non-blocking)

class VisitorEventLog(Base):
    __tablename__ = "visitor_event_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    client_timestamp = Column(DateTime, nullable=True)

    session_id = Column(String)
    fingerprint_id = Column(String)
    event_type = Column(String)
    event_data = Column(String)

    # Enriched metadata fields
    page = Column(String)
    referrer = Column(String)
    device = Column(String)
    ip_address = Column(String)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    organization = Column(String)
    enriched_source = Column(String)
    entropy_data = Column(JSONB)
    user_agent = Column(Text)
    screen_res = Column(String)
    color_depth = Column(String)
    timezone = Column(String)
    language = Column(String)
    platform = Column(String)
    device_memory = Column(String)
    cpu_cores = Column(String)
    gpu_vendor = Column(String)
    gpu_renderer = Column(String)
    canvas_hash = Column(String)
    audio_hash = Column(String)

class VisitorDerivedLog(Base):
    __tablename__ = "visitor_derived_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String)
    fingerprint_id = Column(String)
    visit_type = Column(String)         # "New" or "Returning"
    traffic_type = Column(String)       # "Organic", "Paid", "Social", etc.
    entry_page = Column(String)         # First page visited in the session
    bounced = Column(String)            # "Yes" or "No"
    geo_region_type = Column(String)    # "Domestic" or "International"
    landing_source = Column(String)     # "utm", "referrer", or "direct"
    timestamp = Column(DateTime, default=datetime.utcnow)