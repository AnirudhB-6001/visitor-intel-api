from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    page = Column(String)
    referrer = Column(String)
    device = Column(String)
    session_id = Column(String)
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

    # Fingerprinting
    fingerprint_id = Column(String)

# 🆕 Event log table
class VisitorEventLog(Base):
    __tablename__ = "visitor_event_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String)
    fingerprint_id = Column(String)
    event_type = Column(String)
    event_data = Column(String)