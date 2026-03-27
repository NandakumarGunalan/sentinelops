from datetime import datetime
from pydantic import BaseModel


# --- SecurityEvent ---

class IngestRequest(BaseModel):
    source: str
    event_type: str
    severity: str = "unknown"
    raw_payload: str  # JSON string of the original event


class SecurityEventOut(BaseModel):
    id: int
    source: str
    event_type: str
    severity: str
    received_at: datetime

    model_config = {"from_attributes": True}


# --- Finding ---

class FindingOut(BaseModel):
    id: int
    event_id: int
    title: str
    description: str | None
    priority: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
