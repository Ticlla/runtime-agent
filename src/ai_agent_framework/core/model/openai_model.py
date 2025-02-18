from typing import Dict, Any, Optional
import openai
from .base import BaseModel

class OpenAIModel(BaseModel):
    """OpenAI GPT model implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        **kwargs: Any
    ) -> str:
        """Generate a response using OpenAI's API."""
        try:
            messages = self._prepare_messages(query, context)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            # TODO: Implement proper error handling
            return f"Error generating response: {str(e)}"
    
    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector using OpenAI's API."""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise ValueError(f"Error getting embedding: {str(e)}")
    
    def _prepare_messages(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> list[Dict[str, str]]:
        """Prepare messages for the chat completion API."""
        messages = []
        
        # Add context if available
        if context.get("recent_interactions"):
            for interaction in context["recent_interactions"]:
                messages.append({"role": "user", "content": interaction["query"]})
                messages.append({"role": "assistant", "content": interaction["response"]})
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        return messages 