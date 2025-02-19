import pytest
from unittest.mock import AsyncMock
from ai_agent_framework.core.tools import ToolsManager, BaseTool

class TestTool(BaseTool):
    """Tool de prueba."""
    
    async def execute(self, **params):
        return {"result": "test"}
        
    def get_description(self) -> str:
        return "Test tool description"

@pytest.mark.asyncio
async def test_tools_manager():
    """Test del gestor de herramientas."""
    manager = ToolsManager()
    tool = TestTool()
    
    # Registrar herramienta
    manager.register("test", tool)
    
    # Ejecutar herramienta
    result = await manager.execute_tool("test", value="test_param")
    assert result == {"result": "test"}
    
    # Obtener descripciones
    descriptions = manager.get_tools_description()
    assert len(descriptions) == 1
    assert descriptions[0]["name"] == "test"
    assert descriptions[0]["description"] == "Test tool description" 