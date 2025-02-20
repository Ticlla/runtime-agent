import json
import time
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
from .base import BaseMemory

class RedisMemory(BaseMemory):
    """Redis-based short-term memory."""
    
    def __init__(self, url: str, ttl: int = 3600):
        """Initialize Redis memory."""
        self.url = url
        self.ttl = ttl
        self.client = None
    
    async def initialize(self) -> None:
        """Connect to Redis."""
        self.client = redis.from_url(self.url)
        await self.client.ping()  # Verify connection
    
    async def store_interaction(
        self,
        query: str,
        response: str,
        context: Dict[str, Any]
    ) -> None:
        """Store interaction in Redis."""
        if not self.client:
            raise RuntimeError("Redis not initialized")
            
        interaction = {
            "query": query,
            "response": response,
            "context": context,
            "timestamp": int(time.time())
        }
        
        # Store in recent interactions list
        await self.client.lpush(
            "recent_interactions",
            json.dumps(interaction)
        )
        await self.client.ltrim("recent_interactions", 0, 9)  # Keep last 10
        
        # Set TTL
        await self.client.expire("recent_interactions", self.ttl)
    
    async def retrieve_context(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve recent interactions as context."""
        if not self.client:
            raise RuntimeError("Redis not initialized")
            
        # Get recent interactions
        interactions = await self.client.lrange("recent_interactions", 0, limit - 1)
        recent = [
            json.loads(interaction)
            for interaction in interactions
        ]
        
        return {
            "recent_interactions": recent,
            "memory_type": "short_term"
        }
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close() 