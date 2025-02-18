import pytest
from ai_agent_framework.core.model.factory import ModelFactory
from ai_agent_framework.core.model.ollama_model import OllamaModel
from ai_agent_framework.core.model.openai_model import OpenAIModel

def test_create_ollama_model():
    """Test creation of Ollama model."""
    config = {
        "model_type": "ollama",
        "base_url": "http://localhost:11434",
        "model": "llama2"
    }
    model = ModelFactory.create_model(**config)
    assert isinstance(model, OllamaModel)
    assert model.base_url == "http://localhost:11434"
    assert model.model == "llama2"

def test_create_openai_model():
    """Test creation of OpenAI model."""
    config = {
        "model_type": "openai",
        "api_key": "test_key",
        "model": "gpt-3.5-turbo"
    }
    model = ModelFactory.create_model(**config)
    assert isinstance(model, OpenAIModel)
    assert model.model == "gpt-3.5-turbo"

def test_invalid_model_type():
    """Test error on invalid model type."""
    config = {
        "model_type": "invalid"
    }
    with pytest.raises(ValueError) as exc:
        ModelFactory.create_model(**config)
    assert "Unknown model type" in str(exc.value)

def test_openai_missing_api_key():
    """Test error when OpenAI API key is missing."""
    config = {
        "model_type": "openai"
    }
    with pytest.raises(ValueError) as exc:
        ModelFactory.create_model(**config)
    assert "OpenAI API key is required" in str(exc.value) 