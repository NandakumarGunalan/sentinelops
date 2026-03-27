from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.db import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)          # e.g. "cloudtrail", "siem"
    event_type = Column(String, nullable=False)      # e.g. "login_failure"
    severity = Column(String, default="unknown")     # low / medium / high / critical
    raw_payload = Column(Text, nullable=False)       # original JSON as string
    received_at = Column(DateTime, default=datetime.utcnow)


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("security_events.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(String, default="medium")      # low / medium / high / critical
    status = Column(String, default="open")          # open / in_review / resolved
    created_at = Column(DateTime, default=datetime.utcnow)
