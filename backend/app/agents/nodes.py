import json
import logging
from datetime import datetime
from typing import Dict, Any
from app.agents.state import InvestigationState
from app.config import settings
from app.tools.registry import tool_registry

logger = logging.getLogger(__name__)


def initialize_investigation(state: InvestigationState) -> Dict[str, Any]:
    """Initialize investigation state from alert data"""
    logger.info(f"Initializing investigation for alert {state['alert_id']}")
    
    # Map alert severity to initial risk score
    severity_map = {
        "low": 20,
        "medium": 40,
        "high": 60,
        "critical": 80
    }
    
    alert_severity = state["alert_data"].get("severity", "unknown")
    initial_risk_score = severity_map.get(alert_severity, 30)
    
    reasoning = f"Initialized investigation for {alert_severity} severity alert. Initial risk score: {initial_risk_score}"
    
    return {
        "current_risk_score": initial_risk_score,
        "risk_score_history": [{
            "old_score": 0,
            "new_score": initial_risk_score,
            "justification": f"Initial score based on alert severity: {alert_severity}",
            "timestamp": datetime.utcnow().isoformat()
        }],
        "reasoning_log": [reasoning],
        "status": "running",
        "step_count": state["step_count"] + 1
    }


def analyze_evidence(state: InvestigationState) -> Dict[str, Any]:
    """Analyze accumulated evidence and determine next action"""
    logger.info(f"Analyzing evidence for investigation {state['investigation_id']}")
    
    evidence_count = len(state["evidence"])
    current_risk = state["current_risk_score"]
    
    # Determine if we have sufficient evidence
    # Simple rule: need at least 3 pieces of evidence or risk is critical
    has_sufficient_evidence = evidence_count >= 3 or current_risk >= settings.RISK_THRESHOLD_CRITICAL
    
    if has_sufficient_evidence:
        next_action = "conclude"
        reasoning = f"Sufficient evidence gathered ({evidence_count} pieces). Risk score: {current_risk}. Ready to conclude."
    elif current_risk >= settings.RISK_THRESHOLD_CRITICAL:
        next_action = "escalate"
        reasoning = f"Critical risk threshold exceeded ({current_risk}). Escalating investigation."
    else:
        next_action = "call_tool"
        reasoning = f"Need more evidence ({evidence_count} pieces so far). Risk score: {current_risk}. Continuing investigation."
    
    return {
        "next_action": next_action,
        "reasoning_log": state["reasoning_log"] + [reasoning],
        "step_count": state["step_count"] + 1
    }


def select_tool(state: InvestigationState) -> Dict[str, Any]:
    """Select which tool to invoke based on evidence gaps"""
    logger.info(f"Selecting tool for investigation {state['investigation_id']}")
    
    alert_data = state["alert_data"]
    invoked_tools = [inv["tool_name"] for inv in state["tool_invocations"]]
    
    # Simple deterministic tool selection logic
    # Priority order based on alert type and what hasn't been called yet
    
    tool_priority = []
    
    # Always check IP reputation first if we have a source_ip
    if "source_ip" in alert_data.get("raw_payload", {}) and "ip_reputation_lookup" not in invoked_tools:
        tool_priority.append(("ip_reputation_lookup", {"ip_address": alert_data["raw_payload"]["source_ip"]}))
    
    # Check if user is privileged
    if "user_id" in alert_data.get("raw_payload", {}) and "privileged_user_lookup" not in invoked_tools:
        tool_priority.append(("privileged_user_lookup", {"user_id": alert_data["raw_payload"]["user_id"]}))
    
    # Check for geo anomalies
    if ("user_id" in alert_data.get("raw_payload", {}) and 
        "source_ip" in alert_data.get("raw_payload", {}) and 
        "geo_anomaly_check" not in invoked_tools):
        tool_priority.append(("geo_anomaly_check", {
            "user_id": alert_data["raw_payload"]["user_id"],
            "source_ip": alert_data["raw_payload"]["source_ip"]
        }))
    
    # Look for related alerts
    if "related_alerts_lookup" not in invoked_tools:
        tool_priority.append(("recent_related_alerts_lookup", {
            "alert_type": alert_data.get("event_type", "unknown"),
            "time_window_hours": 24
        }))
    
    # Look up playbooks
    if "playbook_lookup" not in invoked_tools:
        tool_priority.append(("playbook_lookup", {
            "alert_type": alert_data.get("event_type", "unknown"),
            "severity": alert_data.get("severity", "medium")
        }))
    
    # Select first available tool
    if tool_priority:
        selected_tool, parameters = tool_priority[0]
        reasoning = f"Selected tool: {selected_tool} to gather more evidence"
    else:
        # Fallback: conclude if no more tools to call
        return {
            "next_action": "conclude",
            "reasoning_log": state["reasoning_log"] + ["No more tools available to call. Concluding investigation."],
            "step_count": state["step_count"] + 1
        }
    
    return {
        "selected_tool": selected_tool,
        "tool_parameters": parameters,
        "reasoning_log": state["reasoning_log"] + [reasoning],
        "step_count": state["step_count"] + 1
    }


async def invoke_tool(state: InvestigationState) -> Dict[str, Any]:
    """Execute selected tool and gather evidence"""
    tool_name = state["selected_tool"]
    parameters = state["tool_parameters"]
    
    logger.info(f"Invoking tool {tool_name} for investigation {state['investigation_id']}")
    
    start_time = datetime.utcnow()
    
    # Invoke tool via registry
    result = await tool_registry.invoke(tool_name, parameters)
    
    end_time = datetime.utcnow()
    duration_ms = (end_time - start_time).total_seconds() * 1000
    
    # Create tool invocation record
    invocation_record = {
        "tool_name": tool_name,
        "parameters": parameters,
        "result": result.data if result.success else None,
        "timestamp": start_time.isoformat(),
        "duration_ms": duration_ms,
        "error": result.error if not result.success else None
    }
    
    # Update state
    updates = {
        "tool_invocations": state["tool_invocations"] + [invocation_record],
        "step_count": state["step_count"] + 1
    }
    
    if result.success:
        # Add evidence
        updates["evidence"] = state["evidence"] + [result.data]
        updates["reasoning_log"] = state["reasoning_log"] + [
            f"Tool {tool_name} completed successfully. Evidence gathered."
        ]
    else:
        # Log error but continue
        updates["errors"] = state["errors"] + [f"Tool {tool_name} failed: {result.error}"]
        updates["reasoning_log"] = state["reasoning_log"] + [
            f"Tool {tool_name} failed: {result.error}. Continuing with available evidence."
        ]
    
    return updates


def update_risk_score(state: InvestigationState) -> Dict[str, Any]:
    """Recalculate risk score based on new evidence"""
    logger.info(f"Updating risk score for investigation {state['investigation_id']}")
    
    old_score = state["current_risk_score"]
    evidence = state["evidence"]
    
    # Simple risk scoring logic based on evidence
    risk_adjustments = 0
    justifications = []
    
    for ev in evidence:
        # IP reputation increases risk
        if "reputation_score" in ev:
            rep_score = ev["reputation_score"]
            if rep_score > 70:
                risk_adjustments += 15
                justifications.append(f"High IP reputation score ({rep_score})")
            elif rep_score > 40:
                risk_adjustments += 5
                justifications.append(f"Medium IP reputation score ({rep_score})")
        
        # Privileged user increases risk
        if "is_privileged" in ev and ev["is_privileged"]:
            risk_adjustments += 10
            justifications.append("User has privileged access")
        
        # Geo anomaly increases risk
        if "is_anomalous" in ev and ev["is_anomalous"]:
            risk_adjustments += 15
            justifications.append(f"Geographic anomaly detected ({ev.get('distance_km', 0)} km)")
        
        # Multiple related alerts increase risk
        if "count" in ev and ev["count"] > 5:
            risk_adjustments += 10
            justifications.append(f"Multiple related alerts found ({ev['count']})")
    
    new_score = min(100, old_score + risk_adjustments)
    justification = "; ".join(justifications) if justifications else "No significant risk factors found"
    
    return {
        "current_risk_score": new_score,
        "risk_score_history": state["risk_score_history"] + [{
            "old_score": old_score,
            "new_score": new_score,
            "justification": justification,
            "timestamp": datetime.utcnow().isoformat()
        }],
        "reasoning_log": state["reasoning_log"] + [f"Risk score updated: {old_score} -> {new_score}. {justification}"],
        "step_count": state["step_count"] + 1
    }


def check_stopping_conditions(state: InvestigationState) -> Dict[str, Any]:
    """Determine if investigation should continue or terminate"""
    logger.info(f"Checking stopping conditions for investigation {state['investigation_id']}")
    
    step_count = state["step_count"]
    max_steps = state["max_steps"]
    errors = state["errors"]
    current_risk = state["current_risk_score"]
    
    # Check max steps
    if step_count >= max_steps:
        return {
            "status": "max_steps_reached",
            "next_action": "conclude",
            "reasoning_log": state["reasoning_log"] + [f"Maximum steps ({max_steps}) reached. Concluding investigation."],
            "step_count": step_count + 1
        }
    
    # Check for critical errors
    if len(errors) > 3:
        return {
            "status": "failed",
            "next_action": "conclude",
            "reasoning_log": state["reasoning_log"] + ["Too many errors encountered. Marking investigation as failed."],
            "step_count": step_count + 1
        }
    
    # Check if critical risk threshold crossed
    if current_risk >= settings.RISK_THRESHOLD_CRITICAL:
        return {
            "next_action": "escalate",
            "reasoning_log": state["reasoning_log"] + [f"Critical risk threshold ({settings.RISK_THRESHOLD_CRITICAL}) exceeded. Escalating."],
            "step_count": step_count + 1
        }
    
    # Continue investigation
    return {
        "reasoning_log": state["reasoning_log"] + ["Stopping conditions not met. Continuing investigation."],
        "step_count": step_count + 1
    }


def generate_finding(state: InvestigationState) -> Dict[str, Any]:
    """Produce final finding with recommended action"""
    logger.info(f"Generating finding for investigation {state['investigation_id']}")
    
    final_risk_score = state["current_risk_score"]
    alert_data = state["alert_data"]
    evidence = state["evidence"]
    
    # Map risk score to priority
    if final_risk_score >= settings.RISK_THRESHOLD_CRITICAL:
        priority = "critical"
        recommended_action = "escalate_to_human"
    elif final_risk_score >= settings.RISK_THRESHOLD_HIGH:
        priority = "high"
        recommended_action = "block_ip"
    elif final_risk_score >= settings.RISK_THRESHOLD_MEDIUM:
        priority = "medium"
        recommended_action = "isolate_host"
    elif final_risk_score >= settings.RISK_THRESHOLD_LOW:
        priority = "low"
        recommended_action = "monitor"
    else:
        priority = "low"
        recommended_action = "no_action_required"
    
    # Generate finding title
    event_type = alert_data.get("event_type", "security event")
    finding_title = f"{priority.upper()}: {event_type} detected"
    
    # Generate finding description
    evidence_summary = f"Investigation analyzed {len(evidence)} pieces of evidence. "
    evidence_summary += f"Final risk score: {final_risk_score}/100. "
    
    if evidence:
        evidence_summary += "Key findings: "
        findings = []
        for ev in evidence:
            if "reputation_score" in ev:
                findings.append(f"IP reputation score {ev['reputation_score']}")
            if "is_privileged" in ev and ev["is_privileged"]:
                findings.append("privileged user involved")
            if "is_anomalous" in ev and ev["is_anomalous"]:
                findings.append(f"geographic anomaly ({ev.get('distance_km', 0)} km)")
        evidence_summary += ", ".join(findings) + "."
    
    finding_description = evidence_summary
    
    return {
        "status": "completed",
        "recommended_action": recommended_action,
        "finding_title": finding_title,
        "finding_description": finding_description,
        "reasoning_log": state["reasoning_log"] + [f"Finding generated: {finding_title}. Recommended action: {recommended_action}"],
        "step_count": state["step_count"] + 1
    }


def handle_error(state: InvestigationState) -> Dict[str, Any]:
    """Handle investigation failures gracefully"""
    logger.error(f"Handling error for investigation {state['investigation_id']}")
    
    errors = state["errors"]
    error_summary = "; ".join(errors[-3:])  # Last 3 errors
    
    return {
        "status": "failed",
        "finding_title": "Investigation Failed",
        "finding_description": f"Investigation encountered errors and could not complete: {error_summary}",
        "recommended_action": "escalate_to_human",
        "reasoning_log": state["reasoning_log"] + [f"Investigation failed due to errors: {error_summary}"],
        "step_count": state["step_count"] + 1
    }
