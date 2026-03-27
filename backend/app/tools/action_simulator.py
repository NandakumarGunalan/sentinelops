import hashlib
from typing import Dict, Any
from app.tools.registry import BaseTool, ToolResult
from app.config import settings


class ActionSimulatorTool(BaseTool):
    """Tool for simulating execution of response actions"""
    
    VALID_ACTIONS = [
        "no_action_required",
        "monitor",
        "isolate_host",
        "block_ip",
        "escalate_to_human",
        "trigger_automated_response"
    ]
    
    @property
    def name(self) -> str:
        return "action_simulator"
    
    @property
    def description(self) -> str:
        return "Simulate execution of a response action"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "description": "Type of action to simulate",
                    "enum": self.VALID_ACTIONS
                },
                "target": {
                    "type": "string",
                    "description": "Target of action (IP, hostname, etc.)"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If false, actually execute action (requires ENABLE_REAL_ACTIONS)",
                    "default": True
                }
            },
            "required": ["action_type", "target"]
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute action simulation"""
        action_type = parameters.get("action_type")
        target = parameters.get("target")
        dry_run = parameters.get("dry_run", True)
        
        if not action_type or not target:
            return ToolResult(
                success=False,
                error="Missing required parameters: action_type and target"
            )
        
        if action_type not in self.VALID_ACTIONS:
            return ToolResult(
                success=False,
                error=f"Invalid action_type. Must be one of: {', '.join(self.VALID_ACTIONS)}"
            )
        
        # Check if real actions are enabled
        should_simulate = dry_run or not settings.ENABLE_REAL_ACTIONS
        
        # Deterministic success prediction based on target hash
        target_hash = int(hashlib.md5(target.encode()).hexdigest(), 16)
        would_succeed = (target_hash % 100) > 10  # 90% success rate
        
        # Generate impact assessment
        impact_assessments = {
            "no_action_required": "No impact - alert will be logged for reference",
            "monitor": "Low impact - increased monitoring on target for 24 hours",
            "isolate_host": "Medium impact - host will be disconnected from network",
            "block_ip": "Medium impact - IP will be blocked at firewall level",
            "escalate_to_human": "Low impact - alert forwarded to security analyst",
            "trigger_automated_response": "High impact - automated remediation will be executed"
        }
        
        impact_assessment = impact_assessments.get(
            action_type,
            "Unknown impact"
        )
        
        return ToolResult(
            success=True,
            data={
                "action_type": action_type,
                "target": target,
                "simulated": should_simulate,
                "would_succeed": would_succeed,
                "impact_assessment": impact_assessment,
                "real_actions_enabled": settings.ENABLE_REAL_ACTIONS
            }
        )
