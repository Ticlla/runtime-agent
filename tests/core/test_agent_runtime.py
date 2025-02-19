import pytest
from unittest.mock import AsyncMock, MagicMock
from ai_agent_framework.core.agent_runtime import AgentRuntime
from ai_agent_framework.core.memory import BaseMemory
from ai_agent_framework.core.model import BaseModel
from ai_agent_framework.core.tools import ToolsManager

class MockMemory(BaseMemory):
    """Mock memory for testing."""
    async def initialize(self): pass
    async def store_interaction(self, query, response, context, embedding=None): pass
    async def retrieve_context(self, query, embedding=None, limit=5): 
        return {"source": "mock", "recent_interactions": []}
    async def clear(self): pass
    async def close(self): pass

class MockModel(BaseModel):
    """Mock model for testing."""
    async def generate_response(self, query, context=None, tools=None):
        """Mock response generation that accepts tools parameter."""
        return f"Test response for: {query}"
    
    async def get_embedding(self, text):
        return [0.1] * 1536
    
    async def close(self): pass

@pytest.fixture
async def runtime():
    """Fixture for AgentRuntime testing."""
    config = {
        "memory_config": {
            "redis": {"url": "redis://localhost"},
            "postgres": {"url": "postgresql://localhost"}
        },
        "model_config": {"model_type": "test"}
    }
    
    runtime = AgentRuntime(config)
    runtime.short_term = MockMemory()
    runtime.long_term = MockMemory()
    runtime.model = MockModel()
    runtime.tools = ToolsManager()
    
    await runtime.short_term.initialize()
    await runtime.long_term.initialize()
    
    yield runtime
    
    await runtime.close()

@pytest.mark.asyncio
async def test_runtime_initialization():
    """Test runtime initialization."""
    config = {
        "memory_config": {
            "redis": {"url": "redis://localhost"},
            "postgres": {"url": "postgresql://localhost"}
        },
        "model_config": {"model_type": "test"}
    }
    
    runtime = AgentRuntime(config)
    assert isinstance(runtime.tools, ToolsManager)
    assert runtime.short_term is None
    assert runtime.long_term is None

@pytest.mark.asyncio
async def test_process_query(runtime):
    """Test basic query processing."""
    response = await runtime.process_query("test query")
    assert "Test response for:" in response

@pytest.mark.asyncio
async def test_process_query_with_context(runtime):
    """Test query processing with context."""
    context = {"test_key": "test_value"}
    response = await runtime.process_query("test query", context=context)
    assert "Test response for:" in response

@pytest.mark.asyncio
async def test_runtime_process_query_short_term(runtime):
    """Test query processing with short-term memory."""
    response = await runtime.process_query("test query", use_long_term=False)
    assert "Test response for:" in response

@pytest.mark.asyncio
async def test_runtime_process_query_long_term(runtime):
    """Test query processing with long-term memory."""
    response = await runtime.process_query("test query", use_long_term=True)
    assert "Test response for:" in response

@pytest.mark.asyncio
async def test_runtime_error_handling(runtime):
    """Test error handling in runtime."""
    # Make the model fail
    async def mock_error(*args, **kwargs):
        raise Exception("Test error")
    
    runtime.model.generate_response = mock_error
    response = await runtime.process_query("test query")
    assert "Error processing query" in response

@pytest.mark.asyncio
async def test_agent_runtime_initialization():
    """Test AgentRuntime initialization."""
    config = {
        "test_mode": True,
        "model_type": "test",
        "model_config": {},
        "memory_config": {
            "redis": {"url": "redis://localhost"},
            "postgres": {"url": "postgresql://localhost"}
        }
    }
    agent_runtime = AgentRuntime(config)
    
    assert agent_runtime.config == config
    assert agent_runtime.tools is not None
    assert agent_runtime.short_term is None  # No inicializado aún
    assert agent_runtime.long_term is None   # No inicializado aún
    assert agent_runtime.model is None       # No inicializado aún

def test_runtime_initialization():
    """Test runtime initialization."""
    config = {
        "memory_config": {},
        "model_config": {"model_type": "ollama"}
    }
    runtime = AgentRuntime(config)
    assert isinstance(runtime.tools, ToolsManager) 