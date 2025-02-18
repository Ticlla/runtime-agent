import pytest
from ai_agent_framework.core.memory import BaseMemory
from ai_agent_framework.core.model import BaseModel
from ai_agent_framework.core.tools import Tools
from ai_agent_framework.core.tools.base_tool import BaseTool

# Configuración global para pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

class TestMemory(BaseMemory):
    """Memory implementation for testing."""
    async def initialize(self): pass
    async def store_interaction(self, query, response, context, embedding): pass
    async def retrieve_context(self, query, embedding=None, limit=5): 
        return {"source": "test", "recent_interactions": []}
    async def clear(self): pass
    async def close(self): pass

@pytest.fixture
async def memory():
    """Provide a test memory instance."""
    return TestMemory()

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

@pytest.fixture
def tools_manager():
    """Fixture that provides a Tools instance."""
    return Tools()

@pytest.fixture
def mock_tool():
    """Fixture that provides a MockTool instance."""
    return MockTool()

class MockTool(BaseTool):
    """Mock tool for testing."""
    
    async def execute(self, **params):
        return {"result": "test"}
    
    def get_description(self) -> str:
        return "A mock tool for testing" 