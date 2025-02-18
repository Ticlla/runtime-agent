from typing import Dict, Any, List, Optional
from .base_tool import BaseTool

class ToolsManager:
    """Manages the available tools for the agent."""
    
    def __init__(self, **config):
        """
        Initialize tools manager.
        
        Args:
            config: Configuration options for tools
        """
        self.config = config
        self.tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, name: str, tool: BaseTool) -> None:
        """
        Register a new tool.
        
        Args:
            name: Tool identifier
            tool: Tool instance
        """
        self.tools[name] = tool
    
    async def execute_tool(self, name: str, **params: Any) -> Any:
        """
        Execute a tool by name.
        
        Args:
            name: Tool identifier
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
            
        return await self.tools[name].execute(**params)
    
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