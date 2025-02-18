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
    embedding = [0.1] * 1536  # Vector numérico en lugar de string
    
    # Store interaction
    await postgres_memory.store_interaction(query, response, context, embedding)
    
    # Verify storage
    async with postgres_memory.pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM test_memory ORDER BY id DESC LIMIT 1')
        assert row['query'] == query
        assert row['response'] == response
        assert row['context'] == json.dumps(context)

@pytest.mark.asyncio
async def test_retrieve_context_with_embedding(postgres_memory):
    """Test retrieving context with embedding vector."""
    # Test data
    query = "test query"
    response = "test response"
    context = {"test_key": "test_value"}
    embedding = [0.1] * 1536  # Vector de 1536 dimensiones
    
    # Store interaction
    await postgres_memory.store_interaction(query, response, context, embedding)
    
    # Test retrieval with embedding
    result = await postgres_memory.retrieve_context("test", embedding)
    
    assert result["source"] == "postgres"
    assert result["search_type"] == "vector"
    assert result["total_found"] > 0
    assert len(result["recent_interactions"]) > 0
    
    interaction = result["recent_interactions"][0]
    assert interaction["query"] == query
    assert interaction["response"] == response
    assert interaction["context"] == context
    assert "similarity" in interaction
    assert isinstance(interaction["timestamp"], str)

@pytest.mark.asyncio
async def test_retrieve_context_without_embedding(postgres_memory):
    """Test retrieving context without embedding vector."""
    # Test data
    query = "test query"
    response = "test response"
    context = {"test_key": "test_value"}
    
    # Store interaction without embedding
    await postgres_memory.store_interaction(query, response, context)
    
    # Test retrieval without embedding
    result = await postgres_memory.retrieve_context("test")
    
    assert result["source"] == "postgres"
    assert result["search_type"] == "recent"
    assert result["total_found"] > 0
    assert len(result["recent_interactions"]) > 0
    
    interaction = result["recent_interactions"][0]
    assert interaction["query"] == query
    assert interaction["response"] == response
    assert interaction["context"] == context
    assert "similarity" not in interaction
    assert isinstance(interaction["timestamp"], str)

@pytest.mark.asyncio
async def test_store_interaction_error_handling(postgres_memory):
    """Test error handling in store_interaction."""
    # Intentar almacenar con un embedding inválido
    with pytest.raises(ValueError) as exc_info:
        await postgres_memory.store_interaction(
            "test query",
            "test response",
            {"test": True},
            "invalid_embedding"  # Esto debería causar un error
        )
    assert "Error storing interaction" in str(exc_info.value)

@pytest.mark.asyncio
async def test_clear(postgres_memory):
    """Test clearing memory."""
    # Store something first
    embedding = [0.1] * 1536  # Vector numérico en lugar de string
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