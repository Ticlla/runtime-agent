import os
import pytest
from dotenv import load_dotenv
from ai_agent_framework.core.memory import BaseMemory
from ai_agent_framework.core.model import BaseModel
from ai_agent_framework.core.tools import ToolsManager
from ai_agent_framework.core.tools.base_tool import BaseTool

# Configuración global para pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Cargar variables de entorno desde .env antes de ejecutar las pruebas
def pytest_configure(config):
    # Intentar cargar desde la raíz del proyecto
    load_dotenv()
    
    # Si no se encuentra OPENAI_API_KEY, usar una clave de prueba
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing-purposes-only"
        print("WARNING: Using test API key. Tests requiring actual API calls may fail.")

class TestMemory(BaseMemory):
    """Memory implementation for testing."""
    async def store_interaction(self, query, response, context): 
        pass
    async def retrieve_context(self, query, limit=5): 
        return {"source": "test", "recent_interactions": []}
    async def clear(self): 
        pass

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
def tools():
    """Provide a test tools manager instance."""
    return ToolsManager()

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