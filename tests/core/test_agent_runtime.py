import pytest
from unittest.mock import AsyncMock, MagicMock
from ai_agent_framework.core.agent_runtime import AgentRuntime
from ai_agent_framework.core.model import BaseModel
from ai_agent_framework.core.memory import Memory
from ai_agent_framework.core.tools import Tools

class TestModel(BaseModel):
    """Test model implementation."""
    async def generate_response(self, query, context, **kwargs):
        return f"Test response for: {query}"
    
    async def get_embedding(self, text):
        return [0.1, 0.2, 0.3]

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
    # Create mocks
    mock_memory = AsyncMock(spec=Memory)
    mock_memory.retrieve_context.return_value = {"context_data": "test"}
    mock_memory.store_interaction = AsyncMock()
    
    mock_model = TestModel()
    mock_tools = MagicMock(spec=Tools)
    
    # Create agent runtime with mocked components
    config = {
        "test_mode": True,
        "model_type": "test",
        "model_config": {}
    }
    agent_runtime = AgentRuntime(config)
    agent_runtime.memory = mock_memory
    agent_runtime.model = mock_model
    agent_runtime.tools = mock_tools
    
    # Test query processing
    query = "Test query"
    response = await agent_runtime.process_query(query)
    
    # Verify response
    assert isinstance(response, str)
    assert "Test response for: Test query" in response
    
    # Verify memory interactions
    mock_memory.retrieve_context.assert_awaited_once_with(query)
    mock_memory.store_interaction.assert_awaited_once()

@pytest.mark.asyncio
async def test_process_query_with_context():
    """Test query processing with additional context."""
    # Create mocks
    mock_memory = AsyncMock(spec=Memory)
    mock_memory.retrieve_context.return_value = {"memory_context": "test"}
    mock_memory.store_interaction = AsyncMock()
    
    mock_model = TestModel()
    mock_tools = MagicMock(spec=Tools)
    
    # Create agent runtime
    config = {
        "test_mode": True,
        "model_type": "test",
        "model_config": {}
    }
    agent_runtime = AgentRuntime(config)
    agent_runtime.memory = mock_memory
    agent_runtime.model = mock_model
    agent_runtime.tools = mock_tools
    
    # Test query processing with context
    query = "Test query"
    additional_context = {"user_context": "additional"}
    response = await agent_runtime.process_query(query, context=additional_context)
    
    # Verify response
    assert isinstance(response, str)
    assert "Test response for: Test query" in response
    
    # Verify memory interactions with combined context
    mock_memory.retrieve_context.assert_awaited_once_with(query)
    mock_memory.store_interaction.assert_awaited_once()

@pytest.mark.asyncio
async def test_process_query_error_handling():
    """Test error handling in query processing."""
    # Create mock that raises an exception
    mock_memory = AsyncMock(spec=Memory)
    mock_memory.retrieve_context.side_effect = Exception("Test error")
    
    # Create agent runtime with failing memory
    config = {
        "test_mode": True,
        "model_type": "test",
        "model_config": {}
    }
    agent_runtime = AgentRuntime(config)
    agent_runtime.memory = mock_memory
    
    # Test error handling
    response = await agent_runtime.process_query("Test query")
    
    # Verify error response
    assert "Error processing query" in response
    assert "Test error" in response 