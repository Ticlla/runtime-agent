import pytest
import json
import time
from unittest.mock import AsyncMock, patch
from ai_agent_framework.core.memory.redis_memory import RedisMemory

@pytest.fixture
async def redis_memory():
    """Provide a RedisMemory instance."""
    memory = RedisMemory(
        redis_url="redis://localhost:6379",
        namespace="test",
        ttl=3600
    )
    yield memory
    await memory.clear()
    await memory.close()

@pytest.mark.asyncio
@patch('redis.asyncio.Redis.from_url')
async def test_store_and_retrieve_interaction(mock_redis):
    """Test storing and retrieving interactions."""
    # Configure mock Redis client
    mock_client = AsyncMock()
    mock_redis.return_value = mock_client
    
    # Configure mock responses
    stored_data = {}
    
    async def mock_zadd(key, mapping):
        stored_data.update(mapping)
        return len(mapping)
    
    async def mock_zrevrange(key, start, end, withscores=False):
        items = list(stored_data.items())
        items.sort(key=lambda x: x[1], reverse=True)
        selected = items[start:end+1]
        return selected if withscores else [item[0] for item in selected]
    
    mock_client.zadd = AsyncMock(side_effect=mock_zadd)
    mock_client.zrevrange = AsyncMock(side_effect=mock_zrevrange)
    mock_client.expire = AsyncMock(return_value=True)
    
    # Create memory instance
    memory = RedisMemory(
        redis_url="redis://localhost:6379",
        namespace="test",
        ttl=3600
    )
    
    # Test data
    query = "Test query"
    response = "Test response"
    context = {"test_key": "test_value"}
    
    # Store interaction
    await memory.store_interaction(query, response, context)
    
    # Verify store operation
    mock_client.zadd.assert_called_once()
    mock_client.expire.assert_called_once()
    
    # Retrieve context
    result = await memory.retrieve_context(query)
    
    # Verify retrieve operation
    mock_client.zrevrange.assert_called_once()
    
    # Verify result structure
    assert "recent_interactions" in result
    assert len(result["recent_interactions"]) == 1
    
    # Verify interaction data
    interaction = result["recent_interactions"][0]
    assert interaction["query"] == query
    assert interaction["response"] == response
    assert interaction["context"] == context
    assert "timestamp" in interaction
    
    # Clean up
    await memory.close()

@pytest.mark.asyncio
@patch('redis.asyncio.Redis.from_url')
async def test_retrieve_context_limit(mock_redis):
    """Test context retrieval limit."""
    # Configure mock Redis client
    mock_client = AsyncMock()
    mock_redis.return_value = mock_client
    
    # Configure mock responses with storage
    stored_data = {}
    
    async def mock_zadd(key, mapping):
        stored_data.update(mapping)
        return len(mapping)
    
    async def mock_zrevrange(key, start, end, withscores=False):
        items = list(stored_data.items())
        items.sort(key=lambda x: x[1], reverse=True)
        selected = items[start:end+1]
        return selected if withscores else [item[0] for item in selected]
    
    mock_client.zadd = AsyncMock(side_effect=mock_zadd)
    mock_client.zrevrange = AsyncMock(side_effect=mock_zrevrange)
    mock_client.expire = AsyncMock(return_value=True)
    
    # Create memory instance
    memory = RedisMemory(
        redis_url="redis://localhost:6379",
        namespace="test",
        ttl=3600
    )
    
    # Store multiple interactions
    for i in range(10):
        await memory.store_interaction(
            f"Query {i}",
            f"Response {i}",
            {"index": i}
        )
        # Simulate time passing to ensure correct ordering
        time.sleep(0.01)
    
    # Retrieve with limit
    result = await memory.retrieve_context("test", limit=5)
    
    # Verify limit
    assert len(result["recent_interactions"]) == 5
    
    # Verify order (most recent first)
    indices = [int(interaction["context"]["index"]) 
              for interaction in result["recent_interactions"]]
    assert indices == list(range(9, 4, -1))
    
    # Verify Redis operations
    assert mock_client.zadd.call_count == 10
    mock_client.zrevrange.assert_called_once()
    
    # Clean up
    await memory.close()

@pytest.mark.asyncio
@patch('redis.asyncio.Redis.from_url')
async def test_clear_memory(mock_redis):
    """Test memory clearing."""
    # Configure mock Redis client
    mock_client = AsyncMock()
    mock_redis.return_value = mock_client
    
    # Configure mock responses with storage
    stored_data = {}
    
    async def mock_zadd(key, mapping):
        stored_data.update(mapping)
        return len(mapping)
    
    async def mock_zrevrange(key, start, end, withscores=False):
        items = list(stored_data.items())
        items.sort(key=lambda x: x[1], reverse=True)
        selected = items[start:end+1]
        return selected if withscores else [item[0] for item in selected]
    
    async def mock_delete(key):
        stored_data.clear()
        return 1
    
    mock_client.zadd = AsyncMock(side_effect=mock_zadd)
    mock_client.zrevrange = AsyncMock(side_effect=mock_zrevrange)
    mock_client.delete = AsyncMock(side_effect=mock_delete)
    mock_client.expire = AsyncMock(return_value=True)
    
    # Create memory instance
    memory = RedisMemory(
        redis_url="redis://localhost:6379",
        namespace="test",
        ttl=3600
    )
    
    # Store an interaction
    await memory.store_interaction(
        "Test query",
        "Test response",
        {"test": True}
    )
    
    # Verify data was stored
    result_before = await memory.retrieve_context("test")
    assert len(result_before["recent_interactions"]) == 1
    
    # Clear memory
    await memory.clear()
    
    # Verify memory is empty
    result_after = await memory.retrieve_context("test")
    assert len(result_after["recent_interactions"]) == 0
    
    # Verify Redis operations
    mock_client.delete.assert_called_once_with("test:interactions")
    
    # Clean up
    await memory.close() 