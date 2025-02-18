from typing import Dict, Any, List
from .base import BaseModel
from .ollama_model import OllamaModel
from .openai_model import OpenAIModel

class ModelFactory:
    """Factory class for creating model instances."""
    
    @staticmethod
    def create_model(
        model_type: str,
        **config: Dict[str, Any]
    ) -> BaseModel:
        """
        Create and return a model instance based on type.
        
        Args:
            model_type: Type of model to create ("ollama", "openai", "test")
            config: Configuration options for the model
            
        Returns:
            BaseModel: Instance of the requested model
        """
        if model_type == "ollama":
            return OllamaModel(
                base_url=config.get("base_url", "http://localhost:11434"),
                model=config.get("model", "llama2")
            )
        elif model_type == "openai":
            api_key = config.get("api_key")
            if not api_key:
                raise ValueError("OpenAI API key is required")
            return OpenAIModel(
                api_key=api_key,
                model=config.get("model", "gpt-3.5-turbo")
            )
        elif model_type == "test":
            # Test model implementation
            class TestModel(BaseModel):
                async def generate_response(self, query: str, context: Dict[str, Any], **kwargs) -> str:
                    return f"Test response for: {query}"
                
                async def get_embedding(self, text: str) -> List[float]:
                    return [0.1] * 1536
            return TestModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}") 