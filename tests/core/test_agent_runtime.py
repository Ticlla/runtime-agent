import pytest
from unittest.mock import AsyncMock, MagicMock
from ai_agent_framework.core.agent_runtime import AgentRuntime
from ai_agent_framework.core.memory import BaseMemory
from ai_agent_framework.core.model import BaseModel
from ai_agent_framework.core.tools import Tools

class MockMemory(BaseMemory):
    """Mock memory for testing."""
    async def initialize(self) -> None:
        """Initialize mock memory."""
        pass
        
    async def store_interaction(
        self,
        query: str,
        response: str,
        context: dict,
        embedding: str = None
    ) -> None:
        """Mock store interaction."""
        pass
        
    async def retrieve_context(
        self,
        query: str,
        embedding: str = None,
        limit: int = 5
    ) -> dict:
        """Mock retrieve context."""
        return {
            "source": "mock",
            "recent_interactions": []
        }
        
    async def clear(self) -> None:
        """Mock clear memory."""
        pass
        
    async def close(self) -> None:
        """Mock close memory."""
        pass

class MockModel(BaseModel):
    """Mock model for testing."""
    async def generate_response(self, query: str, context: dict = None) -> str:
        """Mock generate response."""
        return f"Test response for: {query}"
        
    async def get_embedding(self, text: str) -> list:
        """Mock get embedding."""
        return [0.1] * 1536
        
    async def close(self) -> None:
        """Mock close model."""
        pass

@pytest.fixture
async def runtime():
    """Fixture para pruebas de AgentRuntime."""
    config = {
        "memory_config": {
            "redis": {
                "redis_url": "redis://localhost:6379",
                "namespace": "test",
                "ttl": 3600
            },
            "postgres": {
                "dsn": "postgresql://admin:admin123@localhost:5432/agent_memory",
                "table_name": "test_memory"
            }
        },
        "model_config": {
            "model_type": "ollama",
            "base_url": "http://localhost:11434",
            "model": "llama2"
        }
    }
    
    # Crear runtime con mocks
    runtime = AgentRuntime(config)
    runtime.short_term = MockMemory()
    runtime.long_term = MockMemory()
    runtime.model = MockModel()
    runtime.tools = Tools()
    
    # Inicializar
    await runtime.initialize()
    
    yield runtime
    await runtime.close()

@pytest.mark.asyncio
async def test_runtime_initialization(runtime):
    """Test runtime initialization."""
    assert runtime.short_term is not None
    assert runtime.long_term is not None
    assert runtime.model is not None
    assert runtime.tools is not None

@pytest.mark.asyncio
async def test_runtime_process_query_short_term(runtime):
    """Test query processing with short-term memory."""
    query = "Test query"
    response = await runtime.process_query(query)
    assert response is not None
    assert "Test response for:" in response

@pytest.mark.asyncio
async def test_runtime_process_query_long_term(runtime):
    """Test query processing with long-term memory."""
    query = "Test query"
    response = await runtime.process_query(query, use_long_term=True)
    assert response is not None
    assert "Test response for:" in response

@pytest.mark.asyncio
async def test_runtime_error_handling(runtime):
    """Test error handling in runtime."""
    # Hacer que el modelo falle
    runtime.model.generate_response = AsyncMock(side_effect=Exception("Test error"))
    response = await runtime.process_query("test")
    assert "Error processing query" in response

@pytest.mark.asyncio
async def test_agent_runtime_initialization():
    """Test AgentRuntime initialization."""
    config = {
        "test_mode": True,
        "model_type": "ollama",
        "model_config": {}
    }
    agent_runtime = AgentRuntime(config)
    
    assert agent_runtime.config == config
    assert agent_runtime.orchestration is not None
    assert agent_runtime.memory is not None
    assert agent_runtime.model is not None
    assert agent_runtime.tools is not None

@pytest.mark.asyncio
async def test_process_query():
    """Test basic query processing."""
    config = {
        "memory_config": {},
        "model_config": {"model_type": "ollama"}
    }
    
    runtime = AgentRuntime(config)
    runtime.short_term = MockMemory()
    runtime.long_term = MockMemory()
    runtime.model = MockModel()
    runtime.tools = Tools()
    
    await runtime.initialize()
    response = await runtime.process_query("Test query")
    assert "Test response for:" in response
    await runtime.close()

@pytest.mark.asyncio
async def test_process_query_with_context():
    """Test query processing with context."""
    config = {
        "memory_config": {},
        "model_config": {"model_type": "ollama"}
    }
    
    runtime = AgentRuntime(config)
    runtime.short_term = MockMemory()
    runtime.long_term = MockMemory()
    runtime.model = MockModel()
    runtime.tools = Tools()
    
    await runtime.initialize()
    context = {"test_key": "test_value"}
    response = await runtime.process_query("Test query", context=context)
    assert "Test response for:" in response
    await runtime.close()

@pytest.mark.asyncio
async def test_process_query_error_handling():
    """Test error handling during query processing."""
    config = {
        "memory_config": {},
        "model_config": {"model_type": "ollama"}
    }
    
    runtime = AgentRuntime(config)
    runtime.short_term = MockMemory()
    runtime.long_term = MockMemory()
    runtime.model = MockModel()
    runtime.tools = Tools()
    
    await runtime.initialize()
    
    # Simular error en el modelo
    async def mock_error(*args, **kwargs):
        raise Exception("Test error")
    
    runtime.model.generate_response = mock_error
    
    response = await runtime.process_query("Test query")
    assert "Error processing query" in response
    
    await runtime.close() 