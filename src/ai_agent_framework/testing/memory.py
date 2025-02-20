from typing import Dict, Any, Optional
from ai_agent_framework.core.memory import BaseMemory

class TestMemory(BaseMemory):
    """Memory implementation for testing."""
    
    def __init__(self):
        """Initialize test memory."""
        self.interactions = []
    
    async def initialize(self) -> None:
        """Initialize memory system."""
        pass
    
    async def store_interaction(
        self,
        query: str,
        response: str,
        context: Optional[Dict] = None
    ) -> None:
        """Store an interaction."""
        self.interactions.append({
            "query": query,
            "response": response,
            "context": context or {}
        })
    
    async def retrieve_context(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve context for testing."""
        return {
            "source": "test_memory",
            "recent_interactions": self.interactions[-limit:] if self.interactions else []
        }
    
    async def clear(self) -> None:
        """Clear test memory."""
        self.interactions = []
    
    async def close(self) -> None:
        """Close test memory."""
        await self.clear() 