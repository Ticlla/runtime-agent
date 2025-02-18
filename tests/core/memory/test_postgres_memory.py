import pytest
import json
from datetime import datetime, timezone
from ai_agent_framework.core.memory.postgres_memory import PostgresMemory

@pytest.fixture
async def postgres_memory():
    """Fixture para PostgresMemory con conexión real."""
    # Crear instancia de PostgresMemory
    memory = PostgresMemory(
        dsn="postgresql://admin:admin123@localhost:5432/agent_memory",
        table_name="test_memory"
    )
    
    # Inicializar
    await memory.initialize()
    
    yield memory
    
    # Cleanup - solo si el pool existe
    if memory.pool:
        await memory.clear()
        await memory.close()

@pytest.mark.asyncio
async def test_initialize(postgres_memory):
    """Test database initialization."""
    async with postgres_memory.pool.acquire() as conn:
        result = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'test_memory'
            )
            """
        )
        assert result is True

@pytest.mark.asyncio
async def test_store_interaction(postgres_memory):
    """Test storing an interaction."""
    # Test data
    query = "test query"
    response = "test response"
    context = {"test_key": "test_value"}
    # Convertir lista a string de array PostgreSQL
    embedding = f"[{','.join(['0.1'] * 1536)}]"
    
    # Store interaction
    await postgres_memory.store_interaction(query, response, context, embedding)
    
    # Verify storage
    async with postgres_memory.pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM test_memory ORDER BY id DESC LIMIT 1')
        assert row['query'] == query
        assert row['response'] == response
        assert row['context'] == json.dumps(context)

@pytest.mark.asyncio
async def test_retrieve_context(postgres_memory):
    """Test retrieving context."""
    # Test data
    query = "test query"
    response = "test response"
    context = {"test_key": "test_value"}
    embedding = f"[{','.join(['0.1'] * 1536)}]"
    
    await postgres_memory.store_interaction(query, response, context, embedding)
    
    # Test retrieval
    result = await postgres_memory.retrieve_context("test", embedding)
    
    assert result["source"] == "postgres"
    assert len(result["recent_interactions"]) > 0
    assert result["recent_interactions"][0]["query"] == query

@pytest.mark.asyncio
async def test_clear(postgres_memory):
    """Test clearing memory."""
    # Store something first
    embedding = f"[{','.join(['0.1'] * 1536)}]"
    await postgres_memory.store_interaction(
        "test", "test", {"test": True}, embedding
    )
    
    # Clear
    await postgres_memory.clear()
    
    # Verify it's empty
    async with postgres_memory.pool.acquire() as conn:
        count = await conn.fetchval('SELECT COUNT(*) FROM test_memory')
        assert count == 0

@pytest.mark.asyncio
async def test_close(postgres_memory):
    """Test closing connection."""
    assert postgres_memory.pool is not None
    await postgres_memory.close()
    assert postgres_memory.pool is None 