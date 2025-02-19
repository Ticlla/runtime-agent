import pytest
from unittest.mock import AsyncMock, MagicMock
from ai_agent_framework.core.agent import Agent
from ai_agent_framework.core.memory import BaseMemory
from ai_agent_framework.core.model import BaseModel
from ai_agent_framework.core.tools import ToolsManager

class MockMemory(BaseMemory):
    async def initialize(self): pass
    async def store_interaction(self, query, response, context, embedding): pass
    async def retrieve_context(self, query, embedding, limit=5): 
        return {"source": "mock", "recent_interactions": []}
    async def clear(self): pass
    async def close(self): pass

class MockModel(BaseModel):
    async def generate_response(self, query, context, **kwargs):
        return f"Response to: {query}"
    async def get_embedding(self, text):
        return [0.1] * 1536
    async def close(self): pass

@pytest.fixture
async def agent():
    """Fixture para pruebas de Agent."""
    memory = MockMemory()
    model = MockModel()
    tools = ToolsManager()
    agent = Agent(memory=memory, model=model, tools=tools)
    await agent.initialize()
    yield agent
    await agent.close()

@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initialization."""
    assert agent.memory is not None
    assert agent.model is not None
    assert agent.tools is not None

@pytest.mark.asyncio
async def test_agent_process_query(agent):
    """Test query processing."""
    query = "Test query"
    response = await agent.process_query(query)
    assert response == f"Response to: {query}"

@pytest.mark.asyncio
async def test_agent_process_query_with_context(agent):
    """Test query processing with context."""
    query = "Test query"
    context = {"test_key": "test_value"}
    response = await agent.process_query(query, context)
    assert response == f"Response to: {query}"

@pytest.mark.asyncio
async def test_agent_error_handling(agent):
    """Test error handling during query processing."""
    # Hacer que el modelo falle
    agent.model.generate_response = AsyncMock(side_effect=Exception("Test error"))
    response = await agent.process_query("test")
    assert "Error processing query" in response 