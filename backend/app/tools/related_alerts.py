from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.tools.registry import BaseTool, ToolResult
from app.models import SecurityEvent
from app.db import SessionLocal


class RelatedAlertsTool(BaseTool):
    """Tool for finding recent related alerts in the database"""
    
    @property
    def name(self) -> str:
        return "recent_related_alerts_lookup"
    
    @property
    def description(self) -> str:
        return "Find similar alerts in recent history"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "alert_type": {
                    "type": "string",
                    "description": "Type of alert to match"
                },
                "time_window_hours": {
                    "type": "integer",
                    "description": "How far back to search (default: 24)",
                    "default": 24
                },
                "source_ip": {
                    "type": "string",
                    "description": "Optional: filter by source IP"
                }
            },
            "required": ["alert_type"]
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute related alerts lookup"""
        alert_type = parameters.get("alert_type")
        time_window_hours = parameters.get("time_window_hours", 24)
        source_ip = parameters.get("source_ip")
        
        if not alert_type:
            return ToolResult(
                success=False,
                error="Missing required parameter: alert_type"
            )
        
        try:
            db: Session = SessionLocal()
            
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Query for related alerts
            query = db.query(SecurityEvent).filter(
                SecurityEvent.event_type == alert_type,
                SecurityEvent.received_at >= time_threshold
            )
            
            # Optional source IP filter
            if source_ip:
                # Note: This is a simple contains check on raw_payload
                # In production, you'd parse the JSON properly
                query = query.filter(SecurityEvent.raw_payload.contains(source_ip))
            
            related_alerts = query.all()
            
            # Format results
            alerts_data = [
                {
                    "id": alert.id,
                    "source": alert.source,
                    "event_type": alert.event_type,
                    "severity": alert.severity,
                    "received_at": alert.received_at.isoformat()
                }
                for alert in related_alerts
            ]
            
            db.close()
            
            return ToolResult(
                success=True,
                data={
                    "related_alerts": alerts_data,
                    "count": len(alerts_data),
                    "time_window_hours": time_window_hours
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Database query failed: {str(e)}"
            )
