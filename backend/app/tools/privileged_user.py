from datetime import datetime, timedelta
from typing import Dict, Any
from app.tools.registry import BaseTool, ToolResult


class PrivilegedUserTool(BaseTool):
    """Tool for checking if a user has privileged access rights"""
    
    # In-memory user database for demo
    PRIVILEGED_USERS = {
        "admin": {"roles": ["admin", "superuser"], "days_since_change": 30},
        "root": {"roles": ["root", "superuser"], "days_since_change": 90},
        "sysadmin": {"roles": ["sysadmin", "operator"], "days_since_change": 15},
        "dbadmin": {"roles": ["database_admin"], "days_since_change": 45},
    }
    
    @property
    def name(self) -> str:
        return "privileged_user_lookup"
    
    @property
    def description(self) -> str:
        return "Check if a user has privileged access rights"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                }
            },
            "required": ["user_id"]
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute privileged user lookup"""
        user_id = parameters.get("user_id")
        
        if not user_id:
            return ToolResult(
                success=False,
                error="Missing required parameter: user_id"
            )
        
        # Check if user is in privileged users database
        user_data = self.PRIVILEGED_USERS.get(user_id)
        
        if user_data:
            is_privileged = True
            roles = user_data["roles"]
            days_ago = user_data["days_since_change"]
        else:
            is_privileged = False
            roles = ["user"]
            days_ago = 0
        
        last_privilege_change = datetime.utcnow() - timedelta(days=days_ago)
        
        return ToolResult(
            success=True,
            data={
                "user_id": user_id,
                "is_privileged": is_privileged,
                "roles": roles,
                "last_privilege_change": last_privilege_change.isoformat()
            }
        )
