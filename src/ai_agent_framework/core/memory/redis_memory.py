import json
import time
from typing import Dict, Any, Optional, List
import redis.asyncio as aioredis
from .base import BaseMemory

class RedisMemory(BaseMemory):
    """Redis-based memory implementation."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        namespace: str = "agent",
        ttl: int = 3600  # 1 hour default TTL
    ):
        """
        Initialize Redis memory.
        
        Args:
            redis_url: Redis connection URL
            namespace: Namespace for Redis keys
            ttl: Time-to-live for memory entries in seconds
        """
        self.redis_url = redis_url
        self.namespace = namespace
        self.ttl = ttl
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        if not self.redis:
            self.redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def store_interaction(
        self,
        query: str,
        response: str,
        context: Dict[str, Any]
    ) -> None:
        """Store an interaction in Redis."""
        await self.connect()
            
        interaction = {
            "query": query,
            "response": response,
            "context": context,
            "timestamp": time.time()
        }
        
        # Store in sorted set by timestamp
        key = f"{self.namespace}:interactions"
        await self.redis.zadd(
            key,
            {json.dumps(interaction): interaction["timestamp"]}
        )
        
        # Set TTL
        await self.redis.expire(key, self.ttl)
    
    async def retrieve_context(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve recent interactions from Redis."""
        await self.connect()
            
        key = f"{self.namespace}:interactions"
        
        # Get recent interactions
        interactions = await self.redis.zrevrange(
            key,
            0,
            limit - 1,
            withscores=True
        )
        
        # Parse interactions
        context_data = []
        for interaction_json, score in interactions:
            interaction = json.loads(interaction_json)
            context_data.append(interaction)
        
        return {
            "recent_interactions": context_data,
            "source": "redis"
        }
    
    async def clear(self) -> None:
        """Clear all memory entries."""
        await self.connect()
        await self.redis.delete(f"{self.namespace}:interactions")
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            await self.redis.connection_pool.disconnect() 