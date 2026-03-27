import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Investigation, InvestigationStep, ToolInvocation, Finding
from app.agents.state import InvestigationState

logger = logging.getLogger(__name__)


def record_investigation_step(
    db: Session,
    investigation_id: int,
    step_number: int,
    step_type: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    reasoning: str
) -> InvestigationStep:
    """Record a single investigation step to database"""
    try:
        step = InvestigationStep(
            investigation_id=investigation_id,
            step_number=step_number,
            step_type=step_type,
            inputs=json.dumps(inputs),
            outputs=json.dumps(outputs),
            reasoning=reasoning,
            timestamp=datetime.utcnow()
        )
        db.add(step)
        db.commit()
        db.refresh(step)
        logger.info(f"Recorded step {step_number} for investigation {investigation_id}")
        return step
    except Exception as e:
        logger.error(f"Failed to record investigation step: {e}")
        db.rollback()
        raise


def record_tool_invocation(
    db: Session,
    step_id: int,
    tool_name: str,
    parameters: Dict[str, Any],
    result: Any,
    duration_ms: float,
    error: str = None
) -> ToolInvocation:
    """Record a tool invocation to database"""
    try:
        invocation = ToolInvocation(
            step_id=step_id,
            tool_name=tool_name,
            parameters=json.dumps(parameters),
            result=json.dumps(result) if result else None,
            duration_ms=duration_ms,
            error=error,
            timestamp=datetime.utcnow()
        )
        db.add(invocation)
        db.commit()
        db.refresh(invocation)
        logger.info(f"Recorded tool invocation {tool_name} for step {step_id}")
        return invocation
    except Exception as e:
        logger.error(f"Failed to record tool invocation: {e}")
        db.rollback()
        raise


def update_investigation_status(
    db: Session,
    investigation_id: int,
    status: str,
    final_risk_score: float = None,
    step_count: int = None
) -> Investigation:
    """Update investigation status and metadata"""
    try:
        investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")
        
        investigation.status = status
        if final_risk_score is not None:
            investigation.final_risk_score = final_risk_score
        if step_count is not None:
            investigation.step_count = step_count
        
        if status in ["completed", "failed", "max_steps_reached"]:
            investigation.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(investigation)
        logger.info(f"Updated investigation {investigation_id} status to {status}")
        return investigation
    except Exception as e:
        logger.error(f"Failed to update investigation status: {e}")
        db.rollback()
        raise


def create_finding(
    db: Session,
    investigation_id: int,
    title: str,
    description: str,
    priority: str,
    recommended_action: str
) -> Finding:
    """Create a finding from investigation results"""
    try:
        finding = Finding(
            investigation_id=investigation_id,
            title=title,
            description=description,
            priority=priority,
            recommended_action=recommended_action,
            status="open",
            created_at=datetime.utcnow()
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        logger.info(f"Created finding {finding.id} for investigation {investigation_id}")
        return finding
    except Exception as e:
        logger.error(f"Failed to create finding: {e}")
        db.rollback()
        raise


def persist_investigation_trace(
    db: Session,
    state: InvestigationState,
    step_records: List[Dict[str, Any]]
) -> None:
    """Persist complete investigation trace to database"""
    try:
        investigation_id = state["investigation_id"]
        
        # Record each step
        for step_record in step_records:
            step = record_investigation_step(
                db=db,
                investigation_id=investigation_id,
                step_number=step_record["step_number"],
                step_type=step_record["step_type"],
                inputs=step_record.get("inputs", {}),
                outputs=step_record.get("outputs", {}),
                reasoning=step_record.get("reasoning", "")
            )
            
            # Record tool invocations for this step
            for tool_inv in step_record.get("tool_invocations", []):
                record_tool_invocation(
                    db=db,
                    step_id=step.id,
                    tool_name=tool_inv["tool_name"],
                    parameters=tool_inv["parameters"],
                    result=tool_inv.get("result"),
                    duration_ms=tool_inv["duration_ms"],
                    error=tool_inv.get("error")
                )
        
        # Update investigation status
        update_investigation_status(
            db=db,
            investigation_id=investigation_id,
            status=state["status"],
            final_risk_score=state["current_risk_score"],
            step_count=state["step_count"]
        )
        
        # Create finding if investigation completed
        if state.get("finding_title"):
            create_finding(
                db=db,
                investigation_id=investigation_id,
                title=state["finding_title"],
                description=state["finding_description"],
                priority=_determine_priority(state["current_risk_score"]),
                recommended_action=state["recommended_action"]
            )
        
        logger.info(f"Persisted complete trace for investigation {investigation_id}")
    
    except Exception as e:
        logger.error(f"Failed to persist investigation trace: {e}")
        raise


def _determine_priority(risk_score: float) -> str:
    """Determine priority from risk score"""
    if risk_score >= 80:
        return "critical"
    elif risk_score >= 60:
        return "high"
    elif risk_score >= 40:
        return "medium"
    else:
        return "low"
