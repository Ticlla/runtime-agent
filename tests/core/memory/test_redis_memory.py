import pytest
from unittest.mock import AsyncMock, patch
import json
from ai_agent_framework.core.memory.redis_memory import RedisMemory

@pytest.fixture
async def redis_memory():
    """Fixture para pruebas de RedisMemory."""
    memory = RedisMemory(
        redis_url="redis://localhost:6379",
        namespace="test",
        ttl=3600
    )
    
    # Mock del cliente Redis
    mock_redis = AsyncMock()
    mock_redis.zadd = AsyncMock(return_value=1)
    mock_redis.zrevrange = AsyncMock(return_value=[
        (json.dumps({
            "query": "test query",
            "response": "test response",
            "context": {"test": True},
            "timestamp": 1234567890
        }), 1234567890)
    ])
    mock_redis.expire = AsyncMock()
    mock_redis.delete = AsyncMock()
    mock_redis.close = AsyncMock()
    mock_redis.connection_pool = AsyncMock()
    mock_redis.connection_pool.disconnect = AsyncMock()
    
    # Patch redis.from_url
    with patch('redis.asyncio.from_url', return_value=mock_redis):
        memory.redis = mock_redis  # Asignar directamente el mock
        yield memory
        await memory.close()

@pytest.mark.asyncio
async def test_store_and_retrieve_interaction(redis_memory):
    """Test storing and retrieving an interaction."""
    # Store interaction
    await redis_memory.store_interaction(
        query="test query",
        response="test response",
        context={"test": True}
    )
    
    # Verify zadd was called
    assert redis_memory.redis.zadd.called
    assert redis_memory.redis.expire.called
    
    # Retrieve interaction
    context = await redis_memory.retrieve_context("test query")
    
    assert context["source"] == "redis"
    assert len(context["recent_interactions"]) > 0

@pytest.mark.asyncio
async def test_retrieve_context_limit(redis_memory):
    """Test retrieving context with limit."""
    context = await redis_memory.retrieve_context("test", limit=3)
    
    # Verify zrevrange was called
    assert redis_memory.redis.zrevrange.called
    assert len(context["recent_interactions"]) > 0

@pytest.mark.asyncio
async def test_clear_memory(redis_memory):
    """Test clearing memory."""
    await redis_memory.clear()
    assert redis_memory.redis.delete.called 