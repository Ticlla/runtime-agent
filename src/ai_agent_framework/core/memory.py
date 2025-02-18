from typing import Dict, Any, Optional
from datetime import datetime, UTC

class Memory:
    """Memory system for storing and retrieving context."""
    
    def __init__(self):
        # Simple in-memory storage for testing
        self._short_term = {}
        self._long_term = {}
    
    async def store_interaction(
        self,
        query: str,
        response: str,
        context: Dict[str, Any]
    ) -> None:
        """Store an interaction in memory."""
        timestamp = datetime.now(UTC).isoformat()
        interaction = {
            "query": query,
            "response": response,
            "context": context,
            "timestamp": timestamp
        }
        self._short_term[timestamp] = interaction
    
    async def retrieve_context(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve relevant context for a query."""
        # Simple implementation for testing
        recent_interactions = list(self._short_term.values())[-limit:]
        return {
            "recent_interactions": recent_interactions,
            "context_type": "short_term"
        } 