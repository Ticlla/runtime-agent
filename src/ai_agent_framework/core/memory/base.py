from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseMemory(ABC):
    """Base class for memory implementations."""
    
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
    async def clear(self) -> None:
        """Clear all memory."""
        pass 