import hashlib
from typing import Dict, Any
from app.tools.registry import BaseTool, ToolResult


class GeoAnomalyTool(BaseTool):
    """Tool for detecting unusual geographic access patterns"""
    
    # Simulated user baseline locations
    USER_BASELINES = {
        "user123": "United States",
        "admin": "United States",
        "user456": "United Kingdom",
        "user789": "Germany",
    }
    
    # Simulated IP to country mapping (deterministic based on IP hash)
    COUNTRIES = [
        "United States", "United Kingdom", "Germany", "France", "China",
        "Russia", "Brazil", "India", "Japan", "Australia"
    ]
    
    @property
    def name(self) -> str:
        return "geo_anomaly_check"
    
    @property
    def description(self) -> str:
        return "Detect unusual geographic access patterns"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                },
                "source_ip": {
                    "type": "string",
                    "description": "IP address of current access"
                }
            },
            "required": ["user_id", "source_ip"]
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute geo anomaly check"""
        user_id = parameters.get("user_id")
        source_ip = parameters.get("source_ip")
        
        if not user_id or not source_ip:
            return ToolResult(
                success=False,
                error="Missing required parameters: user_id and source_ip"
            )
        
        # Get user's expected location
        expected_country = self.USER_BASELINES.get(user_id, "United States")
        
        # Simulate geo-IP lookup using hash
        ip_hash = int(hashlib.md5(source_ip.encode()).hexdigest(), 16)
        actual_country = self.COUNTRIES[ip_hash % len(self.COUNTRIES)]
        
        # Check if anomalous
        is_anomalous = expected_country != actual_country
        
        # Simulate distance calculation
        if is_anomalous:
            distance_km = (ip_hash % 10000) + 1000  # 1000-11000 km
        else:
            distance_km = ip_hash % 500  # 0-500 km
        
        return ToolResult(
            success=True,
            data={
                "user_id": user_id,
                "source_ip": source_ip,
                "is_anomalous": is_anomalous,
                "expected_country": expected_country,
                "actual_country": actual_country,
                "distance_km": distance_km
            }
        )
