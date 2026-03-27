from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class ToolInvocationRecord(TypedDict):
    """Record of a single tool invocation"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    timestamp: str  # ISO format
    duration_ms: float
    error: Optional[str]


class RiskScoreUpdate(TypedDict):
    """Record of a risk score update"""
    old_score: float
    new_score: float
    justification: str
    timestamp: str  # ISO format


class InvestigationState(TypedDict):
    """State maintained across LangGraph workflow"""
    
    # Investigation metadata
    investigation_id: int
    alert_id: int
    alert_data: Dict[str, Any]
    
    # Execution tracking
    step_count: int
    max_steps: int
    status: str  # "running", "completed", "failed", "max_steps_reached"
    
    # Evidence accumulation
    evidence: List[Dict[str, Any]]
    tool_invocations: List[ToolInvocationRecord]
    
    # Risk assessment
    current_risk_score: float
    risk_score_history: List[RiskScoreUpdate]
    
    # Decision tracking
    reasoning_log: List[str]
    next_action: Optional[str]  # "call_tool", "conclude", "escalate"
    selected_tool: Optional[str]
    tool_parameters: Optional[Dict[str, Any]]
    
    # Final output
    recommended_action: Optional[str]
    finding_title: Optional[str]
    finding_description: Optional[str]
    
    # Error handling
    errors: List[str]
