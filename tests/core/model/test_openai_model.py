import pytest
from unittest.mock import AsyncMock, patch
from ai_agent_framework.core.model.openai_model import OpenAIModel

@pytest.mark.asyncio
async def test_openai_model_initialization():
    """Test OpenAI model initialization."""
    model = OpenAIModel(api_key="test-key")
    assert model.model == "gpt-3.5-turbo"

@pytest.mark.asyncio
@patch('openai.AsyncOpenAI')
async def test_generate_response(mock_openai):
    """Test response generation."""
    # Configure mock
    mock_client = AsyncMock()
    mock_openai.return_value = mock_client
    
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content="Test response"))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Test the model
    model = OpenAIModel(api_key="test-key")
    response = await model.generate_response(
        query="Test query",
        context={"recent_interactions": []}
    )
    
    assert response == "Test response"
    mock_client.chat.completions.create.assert_called_once() 