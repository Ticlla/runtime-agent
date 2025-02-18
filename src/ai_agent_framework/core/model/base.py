from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseModel(ABC):
    """Base class for AI model implementations."""
    
    @abstractmethod
    async def generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        **kwargs: Any
    ) -> str:
        """Generate a response using the AI model."""
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text."""
        pass 