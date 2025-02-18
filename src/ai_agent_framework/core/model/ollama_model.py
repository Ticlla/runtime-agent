from typing import Dict, Any, Optional
import httpx
from .base import BaseModel

class OllamaModel(BaseModel):
    """Ollama model implementation."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2"
    ):
        """
        Initialize Ollama model.
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        **kwargs: Any
    ) -> str:
        """Generate a response using Ollama API."""
        try:
            # Prepare the context
            messages = self._prepare_messages(query, context)
            
            # Make API request
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": messages,
                    "stream": False,
                    **kwargs
                }
            )
            await response.raise_for_status()
            
            data = await response.json()
            return data['response']
            
        except Exception as e:
            # TODO: Implement proper error handling
            return f"Error generating response: {str(e)}"
        
    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector using Ollama API."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            await response.raise_for_status()
            
            data = await response.json()
            return data['embedding']
            
        except Exception as e:
            raise ValueError(f"Error getting embedding: {str(e)}")
    
    def _prepare_messages(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """Prepare messages for the Ollama API."""
        messages = []
        
        # Add context if available
        if context.get("recent_interactions"):
            for interaction in context["recent_interactions"]:
                messages.append(f"Human: {interaction['query']}")
                messages.append(f"Assistant: {interaction['response']}")
        
        # Add current query
        messages.append(f"Human: {query}")
        messages.append("Assistant: ")
        
        return "\n".join(messages)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose() 