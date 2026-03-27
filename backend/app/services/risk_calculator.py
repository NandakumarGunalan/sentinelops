import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)


def calculate_initial_risk_score(severity: str) -> float:
    """Calculate initial risk score from alert severity"""
    severity_map = {
        "low": 20.0,
        "medium": 40.0,
        "high": 60.0,
        "critical": 80.0,
        "unknown": 30.0
    }
    return severity_map.get(severity.lower(), 30.0)


def update_risk_score(current_score: float, evidence: List[Dict[str, Any]]) -> tuple[float, str]:
    """
    Update risk score based on accumulated evidence
    
    Returns:
        tuple: (new_score, justification)
    """
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
            distance = ev.get("distance_km", 0)
            if distance > 5000:
                risk_adjustments += 20
                justifications.append(f"Severe geographic anomaly ({distance} km)")
            else:
                risk_adjustments += 10
                justifications.append(f"Geographic anomaly detected ({distance} km)")
        
        # Multiple related alerts increase risk
        if "count" in ev:
            count = ev["count"]
            if count > 10:
                risk_adjustments += 15
                justifications.append(f"Many related alerts found ({count})")
            elif count > 5:
                risk_adjustments += 10
                justifications.append(f"Multiple related alerts found ({count})")
            elif count > 2:
                risk_adjustments += 5
                justifications.append(f"Some related alerts found ({count})")
        
        # Playbook availability (slight decrease if good playbook exists)
        if "recommended_playbook_id" in ev and ev["recommended_playbook_id"]:
            risk_adjustments -= 5
            justifications.append("Response playbook available")
    
    new_score = max(0, min(100, current_score + risk_adjustments))
    justification = "; ".join(justifications) if justifications else "No significant risk factors found"
    
    logger.info(f"Risk score updated: {current_score} -> {new_score}. {justification}")
    
    return new_score, justification


def determine_priority(risk_score: float) -> str:
    """Determine priority level from risk score"""
    if risk_score >= settings.RISK_THRESHOLD_CRITICAL:
        return "critical"
    elif risk_score >= settings.RISK_THRESHOLD_HIGH:
        return "high"
    elif risk_score >= settings.RISK_THRESHOLD_MEDIUM:
        return "medium"
    else:
        return "low"


def determine_recommended_action(risk_score: float) -> str:
    """Determine recommended action from risk score"""
    if risk_score >= settings.RISK_THRESHOLD_CRITICAL:
        return "escalate_to_human"
    elif risk_score >= settings.RISK_THRESHOLD_HIGH:
        return "block_ip"
    elif risk_score >= settings.RISK_THRESHOLD_MEDIUM:
        return "isolate_host"
    elif risk_score >= settings.RISK_THRESHOLD_LOW:
        return "monitor"
    else:
        return "no_action_required"
