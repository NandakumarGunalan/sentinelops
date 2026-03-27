"""
Simplified demo server for SentinelOps hackathon
Uses in-memory data and deterministic mock investigations
"""
import json
import time
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(title="SentinelOps Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
alerts_db = []
investigations_db = []

# Demo alert templates
DEMO_ALERTS = [
    {
        "id": 1,
        "source": "EDR",
        "event_type": "privilege_escalation",
        "severity": "critical",
        "title": "Privileged Account Compromise Detected",
        "description": "User 'admin' executed suspicious commands with elevated privileges from unusual location",
        "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
        "raw_data": {
            "user_id": "admin",
            "source_ip": "185.220.101.45",
            "command": "net user administrator /add",
            "process": "powershell.exe"
        }
    },
    {
        "id": 2,
        "source": "SIEM",
        "event_type": "malware_detected",
        "severity": "high",
        "title": "Suspicious Endpoint Command Execution",
        "description": "Malware-like behavior detected on endpoint WKS-2401",
        "timestamp": (datetime.utcnow() - timedelta(minutes=8)).isoformat(),
        "raw_data": {
            "user_id": "user123",
            "source_ip": "192.168.1.100",
            "hostname": "WKS-2401",
            "file_hash": "a3f8d9e2c1b4567890abcdef12345678",
            "process": "svchost.exe"
        }
    },
    {
        "id": 3,
        "source": "CloudTrail",
        "event_type": "login_failure",
        "severity": "medium",
        "title": "Multiple Failed Login Attempts",
        "description": "User 'user456' failed login 15 times from foreign IP",
        "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
        "raw_data": {
            "user_id": "user456",
            "source_ip": "203.0.113.42",
            "attempts": 15,
            "location": "Unknown"
        }
    }
]

# Initialize with demo alerts
for alert in DEMO_ALERTS:
    alerts_db.append(alert)


def generate_investigation_trace(alert_id: int) -> Dict[str, Any]:
    """Generate deterministic investigation trace for demo"""
    alert = next((a for a in alerts_db if a["id"] == alert_id), None)
    if not alert:
        return None
    
    investigation_id = len(investigations_db) + 1
    
    # Scenario-specific investigation steps
    if alert["event_type"] == "privilege_escalation":
        steps = [
            {
                "step_number": 1,
                "step_type": "initialize",
                "timestamp": alert["timestamp"],
                "reasoning": "Initialized investigation for CRITICAL severity privilege escalation alert",
                "risk_score": 80,
                "tool_invocations": []
            },
            {
                "step_number": 2,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=2)).isoformat(),
                "reasoning": "Checking IP reputation for source 185.220.101.45",
                "risk_score": 80,
                "tool_invocations": [{
                    "tool_name": "ip_reputation_lookup",
                    "parameters": {"ip_address": "185.220.101.45"},
                    "result": {
                        "reputation_score": 92,
                        "threat_categories": ["malware", "botnet", "tor_exit"],
                        "last_seen": "2024-01-15T10:30:00Z"
                    },
                    "duration_ms": 145
                }]
            },
            {
                "step_number": 3,
                "step_type": "risk_update",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=3)).isoformat(),
                "reasoning": "Risk increased: High IP reputation score (92), known malware/botnet source",
                "risk_score": 95,
                "tool_invocations": []
            },
            {
                "step_number": 4,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=4)).isoformat(),
                "reasoning": "Checking if user 'admin' has privileged access",
                "risk_score": 95,
                "tool_invocations": [{
                    "tool_name": "privileged_user_lookup",
                    "parameters": {"user_id": "admin"},
                    "result": {
                        "is_privileged": True,
                        "roles": ["admin", "superuser", "domain_admin"],
                        "last_privilege_change": "2023-12-01T08:00:00Z"
                    },
                    "duration_ms": 89
                }]
            },
            {
                "step_number": 5,
                "step_type": "risk_update",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=5)).isoformat(),
                "reasoning": "CRITICAL: Privileged account compromised from malicious IP",
                "risk_score": 98,
                "tool_invocations": []
            },
            {
                "step_number": 6,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=6)).isoformat(),
                "reasoning": "Checking for geographic anomalies",
                "risk_score": 98,
                "tool_invocations": [{
                    "tool_name": "geo_anomaly_check",
                    "parameters": {"user_id": "admin", "source_ip": "185.220.101.45"},
                    "result": {
                        "is_anomalous": True,
                        "expected_country": "United States",
                        "actual_country": "Russia",
                        "distance_km": 8450
                    },
                    "duration_ms": 112
                }]
            },
            {
                "step_number": 7,
                "step_type": "conclusion",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=7)).isoformat(),
                "reasoning": "Investigation complete. Critical threat confirmed.",
                "risk_score": 98,
                "tool_invocations": []
            }
        ]
        finding = {
            "title": "CRITICAL: Privileged Account Compromise from Malicious IP",
            "description": "Admin account accessed from known malicious IP (185.220.101.45) in Russia, 8450km from expected location. IP has reputation score of 92 and is associated with malware/botnet activity. Immediate action required.",
            "priority": "critical",
            "recommended_action": "escalate_to_human",
            "action_details": "1. Immediately disable admin account\n2. Force password reset\n3. Review all recent admin actions\n4. Block source IP at firewall\n5. Initiate incident response protocol"
        }
    
    elif alert["event_type"] == "malware_detected":
        steps = [
            {
                "step_number": 1,
                "step_type": "initialize",
                "timestamp": alert["timestamp"],
                "reasoning": "Initialized investigation for HIGH severity malware detection",
                "risk_score": 60,
                "tool_invocations": []
            },
            {
                "step_number": 2,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=1)).isoformat(),
                "reasoning": "Looking up response playbook for malware incidents",
                "risk_score": 60,
                "tool_invocations": [{
                    "tool_name": "playbook_lookup",
                    "parameters": {"alert_type": "malware_detected", "severity": "high"},
                    "result": {
                        "playbooks": [{
                            "id": "PB-004",
                            "title": "Malware Containment",
                            "steps": [
                                "Isolate affected host from network",
                                "Run full system scan",
                                "Identify malware variant",
                                "Check for lateral movement"
                            ]
                        }],
                        "recommended_playbook_id": "PB-004"
                    },
                    "duration_ms": 67
                }]
            },
            {
                "step_number": 3,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=2)).isoformat(),
                "reasoning": "Checking for related malware alerts",
                "risk_score": 60,
                "tool_invocations": [{
                    "tool_name": "recent_related_alerts",
                    "parameters": {"alert_type": "malware_detected", "time_window_hours": 24},
                    "result": {
                        "related_alerts": [
                            {"id": 2, "severity": "high", "received_at": alert["timestamp"]},
                            {"id": 45, "severity": "medium", "received_at": (datetime.fromisoformat(alert["timestamp"]) - timedelta(hours=2)).isoformat()}
                        ],
                        "count": 2
                    },
                    "duration_ms": 234
                }]
            },
            {
                "step_number": 4,
                "step_type": "risk_update",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=3)).isoformat(),
                "reasoning": "Multiple related malware alerts found. Potential outbreak.",
                "risk_score": 75,
                "tool_invocations": []
            },
            {
                "step_number": 5,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=4)).isoformat(),
                "reasoning": "Checking IP reputation for affected endpoint",
                "risk_score": 75,
                "tool_invocations": [{
                    "tool_name": "ip_reputation_lookup",
                    "parameters": {"ip_address": "192.168.1.100"},
                    "result": {
                        "reputation_score": 35,
                        "threat_categories": [],
                        "last_seen": None
                    },
                    "duration_ms": 98
                }]
            },
            {
                "step_number": 6,
                "step_type": "conclusion",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=5)).isoformat(),
                "reasoning": "Investigation complete. Malware outbreak detected.",
                "risk_score": 75,
                "tool_invocations": []
            }
        ]
        finding = {
            "title": "HIGH: Malware Outbreak Detected on Multiple Endpoints",
            "description": "Malware detected on WKS-2401 with 2 related alerts in past 24 hours. File hash a3f8d9e2c1b4567890abcdef12345678 identified. Playbook PB-004 (Malware Containment) recommended.",
            "priority": "high",
            "recommended_action": "isolate_host",
            "action_details": "1. Isolate WKS-2401 from network\n2. Run full antivirus scan\n3. Check other endpoints for same file hash\n4. Review user123 recent activity\n5. Apply security patches"
        }
    
    else:  # login_failure
        steps = [
            {
                "step_number": 1,
                "step_type": "initialize",
                "timestamp": alert["timestamp"],
                "reasoning": "Initialized investigation for MEDIUM severity login failure",
                "risk_score": 40,
                "tool_invocations": []
            },
            {
                "step_number": 2,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=1)).isoformat(),
                "reasoning": "Checking IP reputation for source",
                "risk_score": 40,
                "tool_invocations": [{
                    "tool_name": "ip_reputation_lookup",
                    "parameters": {"ip_address": "203.0.113.42"},
                    "result": {
                        "reputation_score": 55,
                        "threat_categories": ["proxy"],
                        "last_seen": "2024-01-10T14:20:00Z"
                    },
                    "duration_ms": 123
                }]
            },
            {
                "step_number": 3,
                "step_type": "risk_update",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=2)).isoformat(),
                "reasoning": "Moderate IP reputation score. Proxy detected.",
                "risk_score": 50,
                "tool_invocations": []
            },
            {
                "step_number": 4,
                "step_type": "tool_call",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=3)).isoformat(),
                "reasoning": "Checking for related login failures",
                "risk_score": 50,
                "tool_invocations": [{
                    "tool_name": "recent_related_alerts",
                    "parameters": {"alert_type": "login_failure", "time_window_hours": 24},
                    "result": {
                        "related_alerts": [{"id": 3, "severity": "medium"}],
                        "count": 1
                    },
                    "duration_ms": 187
                }]
            },
            {
                "step_number": 5,
                "step_type": "conclusion",
                "timestamp": (datetime.fromisoformat(alert["timestamp"]) + timedelta(seconds=4)).isoformat(),
                "reasoning": "Investigation complete. Brute force attempt detected.",
                "risk_score": 50,
                "tool_invocations": []
            }
        ]
        finding = {
            "title": "MEDIUM: Brute Force Login Attempt",
            "description": "User user456 experienced 15 failed login attempts from IP 203.0.113.42 (proxy). Moderate threat level.",
            "priority": "medium",
            "recommended_action": "monitor",
            "action_details": "1. Monitor user456 account for 24 hours\n2. Consider temporary account lockout\n3. Notify user of suspicious activity\n4. Review authentication logs"
        }
    
    investigation = {
        "id": investigation_id,
        "alert_id": alert_id,
        "status": "completed",
        "started_at": alert["timestamp"],
        "completed_at": steps[-1]["timestamp"],
        "final_risk_score": steps[-1]["risk_score"],
        "step_count": len(steps),
        "steps": steps,
        "finding": finding
    }
    
    investigations_db.append(investigation)
    return investigation


@app.get("/health")
def health():
    return {"status": "ok", "mode": "demo"}


@app.get("/api/alerts")
def get_alerts():
    return {"alerts": alerts_db, "total": len(alerts_db)}


@app.get("/api/alerts/{alert_id}")
def get_alert(alert_id: int):
    alert = next((a for a in alerts_db if a["id"] == alert_id), None)
    if not alert:
        return {"error": "Alert not found"}, 404
    return alert


@app.post("/api/alerts/{alert_id}/investigate")
def trigger_investigation(alert_id: int):
    """Trigger investigation for an alert"""
    investigation = generate_investigation_trace(alert_id)
    if not investigation:
        return {"error": "Alert not found"}, 404
    return {"investigation_id": investigation["id"], "status": "completed"}


@app.get("/api/investigations/{investigation_id}")
def get_investigation(investigation_id: int):
    investigation = next((i for i in investigations_db if i["id"] == investigation_id), None)
    if not investigation:
        return {"error": "Investigation not found"}, 404
    return investigation


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SentinelOps Demo Server...")
    print("📊 Loaded 3 demo alerts")
    print("🔗 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
