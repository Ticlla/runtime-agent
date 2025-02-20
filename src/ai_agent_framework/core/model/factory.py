from typing import Dict, Any, List
from .base import BaseModel
from .ollama_model import OllamaModel
from .openai_model import OpenAIModel

class ModelFactory:
    """Factory for creating model instances."""
    
    @staticmethod
    def create_model(config: Dict[str, Any]) -> BaseModel:
        """
        Create a model instance based on configuration.
        
        Args:
            config: Model configuration dictionary containing:
                   - model_type: Type of model (e.g., "openai")
                   - api_key: API key for the service
                   - model: Model name/version
                   - Other model-specific settings
        
        Returns:
            Initialized model instance
        
        Raises:
            ValueError: If model type is not supported
        """
        # Verificar que tenemos la configuración necesaria
        if not config:
            raise ValueError("Model configuration is required")
            
        model_type = config.get("type", "").lower()
        if not model_type:
            raise ValueError("Model type is required in configuration")
        
        if model_type == "openai":
            return OpenAIModel(config=config)
            
        elif model_type == "ollama":
            base_url = config.get("base_url", "http://localhost:11434")
            model_name = config.get("model", "llama2")
            return OllamaModel(base_url=base_url, model=model_name)
            
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    @staticmethod
    def create_test_model() -> BaseModel:
        """
        Create a test model instance.
        
        Returns:
            Test model instance
        """
        # Test model implementation
        class TestModel(BaseModel):
            async def generate_response(self, query: str, context: Dict[str, Any], **kwargs) -> str:
                return f"Test response for: {query}"
            
            async def get_embedding(self, text: str) -> List[float]:
                return [0.1] * 1536
        return TestModel() 