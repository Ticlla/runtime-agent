import pytest
from unittest.mock import AsyncMock
from ai_agent_framework.core.tools import Tools
from ai_agent_framework.core.tools.base_tool import BaseTool

class TestTool(BaseTool):
    """Tool de prueba."""
    
    async def execute(self, **params):
        return {"result": "test"}
        
    def get_description(self) -> str:
        return "Test tool description"

@pytest.fixture
def tools_manager():
    """Fixture para ToolsManager."""
    return Tools()

@pytest.mark.asyncio
async def test_register_and_execute_tool(tools_manager):
    """Test registering and executing a tool."""
    # Register tool
    test_tool = TestTool()
    tools_manager.register_tool("test_tool", test_tool)
    
    # Execute tool
    result = await tools_manager.execute_tool("test_tool")
    assert result == {"result": "test"}

@pytest.mark.asyncio
async def test_tool_not_found(tools_manager):
    """Test executing non-existent tool."""
    with pytest.raises(ValueError) as exc_info:
        await tools_manager.execute_tool("non_existent")
    assert "Tool not found" in str(exc_info.value)

def test_get_tools_description(tools_manager):
    """Test getting tools description."""
    # Register tool
    test_tool = TestTool()
    tools_manager.register_tool("test_tool", test_tool)
    
    # Get descriptions
    descriptions = tools_manager.get_tools_description()
    assert len(descriptions) == 1
    assert descriptions[0]["name"] == "test_tool"
    assert descriptions[0]["description"] == "Test tool description" 