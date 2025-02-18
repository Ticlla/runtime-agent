from typing import Dict, Any
from .base import BaseModel
from .openai_model import OpenAIModel
from .ollama_model import OllamaModel

class ModelFactory:
    """Factory for creating model instances."""
    
    @staticmethod
    def create_model(model_type: str, **kwargs: Any) -> BaseModel:
        """
        Create a model instance based on type.
        
        Args:
            model_type: Type of model to create ('openai', 'ollama', 'test', etc.)
            **kwargs: Model-specific configuration
            
        Returns:
            BaseModel: Instance of the requested model
        """
        if model_type == "openai":
            return OpenAIModel(**kwargs)
        elif model_type == "ollama":
            return OllamaModel(**kwargs)
        elif model_type == "test":
            # Test model implementation
            class TestModel(BaseModel):
                async def generate_response(self, query, context, **kwargs):
                    return f"Test response for: {query}"
                
                async def get_embedding(self, text):
                    return [0.1, 0.2, 0.3]
            return TestModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}") 