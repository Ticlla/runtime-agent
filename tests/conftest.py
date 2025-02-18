import pytest
from ai_agent_framework.core.agent_runtime import AgentRuntime
from ai_agent_framework.core.memory import Memory
from ai_agent_framework.core.model import BaseModel
from ai_agent_framework.core.tools import Tools

# Configuración global para pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
async def memory():
    """Provide a test memory instance."""
    return Memory()

@pytest.fixture
async def model():
    """Provide a test model instance."""
    class TestModel(BaseModel):
        async def generate_response(self, query, context, **kwargs):
            return f"Test response for: {query}"
        
        async def get_embedding(self, text):
            return [0.1, 0.2, 0.3]
    
    return TestModel()

@pytest.fixture
async def agent_runtime():
    """Provide a test agent runtime instance."""
    config = {
        "test_mode": True,
        "model_type": "ollama",
        "model_config": {}
    }
    return AgentRuntime(config) 