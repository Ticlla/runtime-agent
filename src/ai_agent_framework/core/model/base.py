from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseModel(ABC):
    """Base class for all models."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize base model with configuration."""
        self.config = config
    
    @abstractmethod
    async def generate_response(
        self, 
        query: str, 
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate response from the model.
        
        Args:
            query: Input query or prompt
            context: Optional context information
            
        Returns:
            Generated response
        """
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.
        
        Args:
            text: Input text
            
        Returns:
            List of embedding values
        """
        pass
    
    async def close(self) -> None:
        """Clean up resources."""
        pass 