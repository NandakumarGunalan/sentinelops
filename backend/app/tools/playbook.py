from typing import Dict, Any, List
from app.tools.registry import BaseTool, ToolResult


class PlaybookTool(BaseTool):
    """Tool for finding recommended response playbooks"""
    
    # Static playbook database
    PLAYBOOKS = {
        "login_failure": [
            {
                "id": "PB-001",
                "title": "Failed Login Investigation",
                "severity": ["medium", "high", "critical"],
                "steps": [
                    "Check user account status",
                    "Review recent login history",
                    "Check for brute force patterns",
                    "Verify source IP reputation",
                    "Consider account lockout if threshold exceeded"
                ]
            }
        ],
        "privilege_escalation": [
            {
                "id": "PB-002",
                "title": "Privilege Escalation Response",
                "severity": ["high", "critical"],
                "steps": [
                    "Immediately review user permissions",
                    "Check for unauthorized privilege changes",
                    "Review audit logs for suspicious activity",
                    "Isolate affected account if necessary",
                    "Escalate to security team"
                ]
            }
        ],
        "data_exfiltration": [
            {
                "id": "PB-003",
                "title": "Data Exfiltration Containment",
                "severity": ["critical"],
                "steps": [
                    "Block suspicious network connections",
                    "Identify affected data sources",
                    "Review user access patterns",
                    "Preserve evidence for forensics",
                    "Notify incident response team immediately"
                ]
            }
        ],
        "malware_detected": [
            {
                "id": "PB-004",
                "title": "Malware Containment",
                "severity": ["high", "critical"],
                "steps": [
                    "Isolate affected host from network",
                    "Run full system scan",
                    "Identify malware variant",
                    "Check for lateral movement",
                    "Initiate remediation procedures"
                ]
            }
        ]
    }
    
    @property
    def name(self) -> str:
        return "playbook_lookup"
    
    @property
    def description(self) -> str:
        return "Find recommended response playbooks for alert type"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "alert_type": {
                    "type": "string",
                    "description": "Type of security alert"
                },
                "severity": {
                    "type": "string",
                    "description": "Alert severity level",
                    "enum": ["low", "medium", "high", "critical"]
                }
            },
            "required": ["alert_type", "severity"]
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute playbook lookup"""
        alert_type = parameters.get("alert_type")
        severity = parameters.get("severity")
        
        if not alert_type or not severity:
            return ToolResult(
                success=False,
                error="Missing required parameters: alert_type and severity"
            )
        
        # Find matching playbooks
        playbooks = self.PLAYBOOKS.get(alert_type, [])
        
        # Filter by severity
        matching_playbooks = [
            pb for pb in playbooks
            if severity in pb.get("severity", [])
        ]
        
        # Determine recommended playbook
        recommended_playbook_id = None
        if matching_playbooks:
            recommended_playbook_id = matching_playbooks[0]["id"]
        
        return ToolResult(
            success=True,
            data={
                "alert_type": alert_type,
                "severity": severity,
                "playbooks": matching_playbooks,
                "recommended_playbook_id": recommended_playbook_id,
                "playbooks_found": len(matching_playbooks)
            }
        )
