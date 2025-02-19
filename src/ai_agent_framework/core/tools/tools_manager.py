from typing import Dict, Any, List
from .base_tool import BaseTool

class ToolsManager:
    """Manages the available tools for the agent."""
    
    def __init__(self):
        """Initialize tools manager."""
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, name: str, tool: BaseTool) -> None:
        """
        Register a new tool.
        
        Args:
            name: Tool identifier
            tool: Tool instance
        """
        self.tools[name] = tool
    
    async def execute_tool(self, tool_name: str, **params: Any) -> Any:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Tool identifier
            params: Tool parameters
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool_name is not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        return await self.tools[tool_name].execute(**params)
    
    def get_tools_description(self) -> List[Dict[str, str]]:
        """
        Get descriptions of all available tools.
        
        Returns:
            List of dicts containing tool names and descriptions
        """
        return [
            {
                "name": name,
                "description": tool.get_description()
            }
            for name, tool in self.tools.items()
        ] 