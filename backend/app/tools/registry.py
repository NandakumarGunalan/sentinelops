import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """Result of a tool execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseTool(ABC):
    """Base class for all investigation tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable tool description"""
        pass
    
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON schema for tool parameters"""
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute tool with given parameters"""
        pass
    
    @property
    def timeout_seconds(self) -> int:
        """Maximum execution time"""
        return 10


class ToolRegistry:
    """Registry for managing and invoking tools"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool in the registry"""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema
            }
            for tool in self._tools.values()
        ]
    
    async def invoke(self, name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Invoke a tool with timeout and error handling"""
        tool = self.get_tool(name)
        if not tool:
            logger.error(f"Tool not found: {name}")
            return ToolResult(success=False, error=f"Tool {name} not found")
        
        try:
            logger.info(f"Invoking tool: {name} with parameters: {parameters}")
            result = await asyncio.wait_for(
                tool.execute(parameters),
                timeout=tool.timeout_seconds
            )
            logger.info(f"Tool {name} completed successfully")
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Tool {name} timed out after {tool.timeout_seconds}s")
            return ToolResult(
                success=False,
                error=f"Tool execution timed out after {tool.timeout_seconds}s"
            )
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )


# Global tool registry instance
tool_registry = ToolRegistry()
