import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Investigation, InvestigationStep, ToolInvocation
from app.schemas import InvestigationTraceResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


@router.get("/{investigation_id}/trace", response_model=InvestigationTraceResponse)
def get_investigation_trace(investigation_id: int, db: Session = Depends(get_db)):
    """Retrieve complete execution trace for an investigation"""
    
    # Get investigation
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail=f"Investigation {investigation_id} not found")
    
    # Get all steps with tool invocations
    steps = db.query(InvestigationStep).filter(
        InvestigationStep.investigation_id == investigation_id
    ).order_by(InvestigationStep.step_number).all()
    
    # Build trace
    trace_steps = []
    for step in steps:
        # Get tool invocations for this step
        tool_invocations = db.query(ToolInvocation).filter(
            ToolInvocation.step_id == step.id
        ).all()
        
        tool_inv_data = []
        for inv in tool_invocations:
            tool_inv_data.append({
                "tool_name": inv.tool_name,
                "parameters": json.loads(inv.parameters) if inv.parameters else {},
                "result": json.loads(inv.result) if inv.result else None,
                "duration_ms": inv.duration_ms,
                "error": inv.error,
                "timestamp": inv.timestamp.isoformat()
            })
        
        trace_steps.append({
            "step_number": step.step_number,
            "step_type": step.step_type,
            "timestamp": step.timestamp.isoformat(),
            "inputs": json.loads(step.inputs) if step.inputs else {},
            "outputs": json.loads(step.outputs) if step.outputs else {},
            "reasoning": step.reasoning,
            "tool_invocations": tool_inv_data
        })
    
    return {
        "investigation_id": investigation.id,
        "alert_id": investigation.alert_id,
        "status": investigation.status,
        "started_at": investigation.started_at.isoformat(),
        "completed_at": investigation.completed_at.isoformat() if investigation.completed_at else None,
        "final_risk_score": investigation.final_risk_score,
        "step_count": investigation.step_count,
        "trace": trace_steps
    }
