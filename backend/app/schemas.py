from datetime import datetime
from typing import List, Dict, Any, Optional
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


class AlertIngestResponse(BaseModel):
    alert_id: int
    investigation_id: Optional[int]
    status: str
    message: str


# --- Investigation ---

class ToolInvocationResponse(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any]
    duration_ms: float
    error: Optional[str]
    timestamp: str


class InvestigationStepResponse(BaseModel):
    step_number: int
    step_type: str
    timestamp: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    reasoning: str
    tool_invocations: List[ToolInvocationResponse]


class InvestigationTraceResponse(BaseModel):
    investigation_id: int
    alert_id: int
    status: str
    started_at: str
    completed_at: Optional[str]
    final_risk_score: Optional[float]
    step_count: int
    trace: List[InvestigationStepResponse]


# --- Finding ---

class FindingOut(BaseModel):
    id: int
    investigation_id: int
    title: str
    description: str | None
    priority: str
    recommended_action: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
