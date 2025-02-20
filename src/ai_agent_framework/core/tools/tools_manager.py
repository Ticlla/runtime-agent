from typing import Dict, Any, List, Optional
from .base import BaseTool

class ToolsManager:
    """Manager for tool registration and execution."""
    
    def __init__(self):
        """Initialize tools manager."""
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, name: str, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[name] = tool
    
    def get_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a specific tool by name."""
        return self._tools.get(name)
    
    async def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return await tool.execute(**kwargs)
    
    def get_tools_description(self) -> Dict[str, str]:
        """Get descriptions of all registered tools."""
        return {
            name: tool.get_description() 
            for name, tool in self._tools.items()
        } 