import json
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import SecurityEvent, Investigation
from app.agents.triage_agent import triage_workflow
from app.agents.state import InvestigationState
from app.services.trace_recorder import persist_investigation_trace
from app.config import settings

logger = logging.getLogger(__name__)


async def run_investigation(db: Session, alert_id: int) -> Investigation:
    """Launch and execute a complete investigation workflow"""
    try:
        # Get alert data
        alert = db.query(SecurityEvent).filter(SecurityEvent.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        # Create investigation record
        investigation = Investigation(
            alert_id=alert_id,
            status="running",
            step_count=0
        )
        db.add(investigation)
        db.commit()
        db.refresh(investigation)
        
        logger.info(f"Starting investigation {investigation.id} for alert {alert_id}")
        
        # Parse alert payload
        try:
            raw_payload = json.loads(alert.raw_payload)
        except:
            raw_payload = {"raw": alert.raw_payload}
        
        # Initialize investigation state
        initial_state: InvestigationState = {
            "investigation_id": investigation.id,
            "alert_id": alert_id,
            "alert_data": {
                "source": alert.source,
                "event_type": alert.event_type,
                "severity": alert.severity,
                "raw_payload": raw_payload
            },
            "step_count": 0,
            "max_steps": settings.MAX_INVESTIGATION_STEPS,
            "status": "running",
            "evidence": [],
            "tool_invocations": [],
            "current_risk_score": 0.0,
            "risk_score_history": [],
            "reasoning_log": [],
            "next_action": None,
            "selected_tool": None,
            "tool_parameters": None,
            "recommended_action": None,
            "finding_title": None,
            "finding_description": None,
            "errors": []
        }
        
        # Execute LangGraph workflow
        logger.info(f"Executing triage workflow for investigation {investigation.id}")
        final_state = await triage_workflow.ainvoke(initial_state)
        
        logger.info(f"Workflow completed for investigation {investigation.id}. Status: {final_state['status']}")
        
        # Convert state to step records for persistence
        step_records = _convert_state_to_steps(final_state)
        
        # Persist complete trace to database
        persist_investigation_trace(db, final_state, step_records)
        
        # Refresh investigation to get updated data
        db.refresh(investigation)
        
        logger.info(f"Investigation {investigation.id} completed successfully")
        return investigation
    
    except Exception as e:
        logger.error(f"Investigation failed: {e}", exc_info=True)
        
        # Mark investigation as failed
        if investigation:
            investigation.status = "failed"
            investigation.step_count = initial_state.get("step_count", 0)
            db.commit()
        
        raise


def _convert_state_to_steps(state: InvestigationState) -> list:
    """Convert investigation state to step records for database persistence"""
    step_records = []
    reasoning_log = state.get("reasoning_log", [])
    tool_invocations = state.get("tool_invocations", [])
    
    # Create a step record for each reasoning entry
    for i, reasoning in enumerate(reasoning_log, start=1):
        # Find tool invocations that belong to this step
        # This is a simplified approach - in production you'd track this more precisely
        step_tools = []
        if i <= len(tool_invocations):
            step_tools = [tool_invocations[i-1]]
        
        step_records.append({
            "step_number": i,
            "step_type": _infer_step_type(reasoning),
            "inputs": {},
            "outputs": {},
            "reasoning": reasoning,
            "tool_invocations": step_tools
        })
    
    return step_records


def _infer_step_type(reasoning: str) -> str:
    """Infer step type from reasoning text"""
    reasoning_lower = reasoning.lower()
    
    if "initialized" in reasoning_lower or "initializing" in reasoning_lower:
        return "initialize_investigation"
    elif "analyzing evidence" in reasoning_lower:
        return "analyze_evidence"
    elif "selected tool" in reasoning_lower:
        return "select_tool"
    elif "tool" in reasoning_lower and "completed" in reasoning_lower:
        return "invoke_tool"
    elif "risk score updated" in reasoning_lower:
        return "update_risk_score"
    elif "stopping conditions" in reasoning_lower:
        return "check_stopping_conditions"
    elif "finding generated" in reasoning_lower:
        return "generate_finding"
    else:
        return "unknown"
