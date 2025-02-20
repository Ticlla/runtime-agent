from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseMemory(ABC):
    """Base class for memory systems."""
    
    @abstractmethod
    async def store_interaction(
        self,
        query: str,
        response: str,
        context: Dict[str, Any]
    ) -> None:
        """Store an interaction in memory."""
        pass
    
    @abstractmethod
    async def retrieve_context(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve relevant context for a query."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize memory system."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        pass 