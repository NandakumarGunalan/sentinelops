import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any
from app.tools.registry import BaseTool, ToolResult


class IPReputationTool(BaseTool):
    """Tool for checking IP address reputation using deterministic hash-based scoring"""
    
    @property
    def name(self) -> str:
        return "ip_reputation_lookup"
    
    @property
    def description(self) -> str:
        return "Check if an IP address has known malicious activity"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ip_address": {
                    "type": "string",
                    "description": "IP address to check"
                }
            },
            "required": ["ip_address"]
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute IP reputation lookup with deterministic scoring"""
        ip_address = parameters.get("ip_address")
        
        if not ip_address:
            return ToolResult(
                success=False,
                error="Missing required parameter: ip_address"
            )
        
        # Deterministic hash-based scoring for demo
        hash_value = int(hashlib.md5(ip_address.encode()).hexdigest(), 16)
        reputation_score = hash_value % 101  # 0-100
        
        # Determine threat categories based on score
        threat_categories = []
        if reputation_score > 80:
            threat_categories = ["malware", "botnet"]
        elif reputation_score > 60:
            threat_categories = ["spam", "suspicious"]
        elif reputation_score > 40:
            threat_categories = ["proxy"]
        
        # Simulate last_seen timestamp
        days_ago = (hash_value % 30) + 1
        last_seen = datetime.utcnow() - timedelta(days=days_ago)
        
        return ToolResult(
            success=True,
            data={
                "ip_address": ip_address,
                "reputation_score": reputation_score,
                "threat_categories": threat_categories,
                "last_seen": last_seen.isoformat()
            }
        )
