from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """Base class for all tools."""
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dictionary containing tool execution results
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get tool description.
        
        Returns:
            String describing the tool's functionality
        """
        pass
    
    async def initialize(self) -> None:
        """Initialize tool resources if needed."""
        pass
    
    async def cleanup(self) -> None:
        """Clean up tool resources if needed.""" 