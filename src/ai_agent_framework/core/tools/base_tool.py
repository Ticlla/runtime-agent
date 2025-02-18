from typing import Any
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Base class for tools."""
    
    @abstractmethod
    async def execute(self, **params: Any) -> Any:
        """
        Execute the tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get tool description for the agent.
        
        Returns:
            String describing the tool's capabilities
        """
        pass 