from typing import Dict, Any, List, Optional
import openai
from .base import BaseModel
from openai import OpenAI
import json

class OpenAIModel(BaseModel):
    """OpenAI model implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI model."""
        super().__init__(config)
        self.client = OpenAI(api_key=config["api_key"])
        self.model = config.get("model", "gpt-3.5-turbo")
        self.system_prompt = config.get("system_prompt", "You are a helpful assistant.")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 500)
    
    async def generate_response(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate response using OpenAI API."""
        try:
            print("Preparing OpenAI request...")  # Debug
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ]
            
            print("Calling OpenAI API...")  # Debug
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Forzar respuesta JSON
            )
            
            print("Got response from OpenAI")  # Debug
            
            # Verificar y parsear la respuesta JSON
            content = response.choices[0].message.content
            try:
                # Intentar parsear como JSON
                json_response = json.loads(content)
                return json_response
            except json.JSONDecodeError:
                # Si falla, devolver un JSON con el error
                return {
                    "error": "invalid_json",
                    "raw_response": content
                }
                
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")  # Debug
            return {
                "error": "api_error",
                "message": str(e)
            }
    
    async def analyze_code(self, code: str, **kwargs) -> Dict:
        """
        Analyze code using OpenAI.
        
        Args:
            code: Source code to analyze
            kwargs: Additional parameters
            
        Returns:
            Dictionary with analysis results
        """
        prompt = f"""
        Please analyze this Python code and provide a detailed review:

        ```python
        {code}
        ```

        Focus on:
        1. Code structure and organization
        2. Potential bugs and issues
        3. Style and formatting
        4. Security concerns
        5. Performance considerations
        6. Best practices

        Provide the analysis in JSON format with these sections.
        """
        
        try:
            response = await self.generate_response(prompt, {})
            # Convertir la respuesta a diccionario
            # (Aquí podrías usar json.loads si la respuesta está bien formateada)
            return {
                "analysis": response,
                "model": self.model
            }
            
        except Exception as e:
            raise RuntimeError(f"Code analysis failed: {str(e)}")

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector using OpenAI's API."""
        try:
            response = self.client.embeddings.create(
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
    ) -> List[Dict[str, str]]:
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
    
    async def close(self) -> None:
        """Clean up resources."""
        pass  # No cleanup needed for OpenAI 