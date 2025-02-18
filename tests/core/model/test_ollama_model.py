import pytest
from unittest.mock import AsyncMock, patch
from ai_agent_framework.core.model.ollama_model import OllamaModel

@pytest.mark.asyncio
async def test_ollama_model_initialization():
    """Test Ollama model initialization."""
    model = OllamaModel()
    assert model.model == "llama2"
    assert model.base_url == "http://localhost:11434"

@pytest.mark.asyncio
async def test_generate_response():
    """Test response generation."""
    # Create mock response
    mock_response = AsyncMock()
    mock_response.json.return_value = {"response": "Test response"}
    mock_response.raise_for_status = AsyncMock()
    
    # Create mock client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    # Create model with mocked client
    model = OllamaModel()
    model.client = mock_client
    
    # Test the model
    response = await model.generate_response(
        query="Test query",
        context={"recent_interactions": []}
    )
    
    # Verify response
    assert response == "Test response"
    
    # Verify API call
    mock_client.post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": "Human: Test query\nAssistant: ",
            "stream": False
        }
    )
    
    # Verify raise_for_status was called
    mock_response.raise_for_status.assert_awaited_once()
    
    # Clean up
    await model.close()

@pytest.mark.asyncio
async def test_generate_response_with_context():
    """Test response generation with context."""
    # Create mock response
    mock_response = AsyncMock()
    mock_response.json.return_value = {"response": "Test response"}
    mock_response.raise_for_status = AsyncMock()
    
    # Create mock client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    # Create model with mocked client
    model = OllamaModel()
    model.client = mock_client
    
    # Test context
    context = {
        "recent_interactions": [
            {
                "query": "Previous query",
                "response": "Previous response"
            }
        ]
    }
    
    # Test the model
    response = await model.generate_response(
        query="Test query",
        context=context
    )
    
    # Verify response
    assert response == "Test response"
    
    # Verify API call includes context
    expected_prompt = (
        "Human: Previous query\n"
        "Assistant: Previous response\n"
        "Human: Test query\n"
        "Assistant: "
    )
    
    mock_client.post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": expected_prompt,
            "stream": False
        }
    )
    
    # Clean up
    await model.close()

@pytest.mark.asyncio
async def test_generate_response_error():
    """Test error handling in response generation."""
    # Create mock client that raises an exception
    mock_client = AsyncMock()
    mock_client.post.side_effect = Exception("Test error")
    
    # Create model with mocked client
    model = OllamaModel()
    model.client = mock_client
    
    # Test the model
    response = await model.generate_response(
        query="Test query",
        context={}
    )
    
    # Verify error response
    assert "Error generating response" in response
    assert "Test error" in response
    
    # Clean up
    await model.close()

@pytest.mark.asyncio
async def test_get_embedding():
    """Test embedding generation."""
    # Create mock response
    mock_response = AsyncMock()
    mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
    mock_response.raise_for_status = AsyncMock()
    
    # Create mock client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    # Create model with mocked client
    model = OllamaModel()
    model.client = mock_client
    
    # Test the model
    embedding = await model.get_embedding("Test text")
    
    # Verify response
    assert embedding == [0.1, 0.2, 0.3]
    
    # Verify API call
    mock_client.post.assert_called_once_with(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "llama2",
            "prompt": "Test text"
        }
    )
    
    # Verify raise_for_status was called
    mock_response.raise_for_status.assert_awaited_once()
    
    # Clean up
    await model.close()

@pytest.mark.asyncio
async def test_get_embedding_error():
    """Test error handling in embedding generation."""
    # Create mock client that raises an exception
    mock_client = AsyncMock()
    mock_client.post.side_effect = Exception("Test error")
    
    # Create model with mocked client
    model = OllamaModel()
    model.client = mock_client
    
    # Test the model
    with pytest.raises(ValueError) as exc_info:
        await model.get_embedding("Test text")
    
    # Verify error message
    assert "Error getting embedding: Test error" in str(exc_info.value)
    
    # Clean up
    await model.close() 