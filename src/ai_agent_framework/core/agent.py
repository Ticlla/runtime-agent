from typing import Dict, Any, Optional, List
from .memory import BaseMemory
from .model import BaseModel
from .tools import Tools

class Agent:
    """Base Agent class that handles interactions and decision making."""
    
    def __init__(
        self,
        memory: BaseMemory,
        model: BaseModel,
        tools: Tools,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the agent.
        
        Args:
            memory: Memory system implementation
            model: AI model implementation
            tools: Tools available to the agent
            config: Additional configuration options
        """
        self.memory = memory
        self.model = model
        self.tools = tools
        self.config = config or {}
        
    async def initialize(self) -> None:
        """Initialize agent components."""
        await self.memory.initialize()
        
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a user query and generate a response.
        
        Args:
            query: User's input query
            context: Additional context for the query
            
        Returns:
            Generated response
        """
        try:
            # Get embedding for the query
            embedding = await self.model.get_embedding(query)
            
            # Retrieve relevant context
            memory_context = await self.memory.retrieve_context(
                query=query,
                embedding=embedding
            )
            
            # Combine contexts
            full_context = {
                **(context or {}),
                **memory_context
            }
            
            # Generate response
            response = await self.model.generate_response(
                query=query,
                context=full_context
            )
            
            # Store interaction
            await self.memory.store_interaction(
                query=query,
                response=response,
                context=full_context,
                embedding=embedding
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            # TODO: Add proper logging
            print(error_msg)
            return error_msg
            
    async def close(self) -> None:
        """Cleanup and close agent components."""
        await self.memory.close()
        await self.model.close() 