from typing import Dict, Any, Optional
from .memory import BaseMemory
from .model import ModelFactory
from .tools import ToolsManager

class AgentRuntime:
    """Runtime environment for AI agents."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the runtime.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.short_term: Optional[BaseMemory] = None
        self.long_term: Optional[BaseMemory] = None
        self.model = None
        self.tools = ToolsManager()
    
    async def initialize(self) -> None:
        """Initialize runtime components."""
        # Initialize memory systems
        memory_config = self.config.get("memory_config", {})
        
        # Initialize short-term memory (Redis)
        if "redis" in memory_config:
            from .memory.redis_memory import RedisMemory
            self.short_term = RedisMemory(**memory_config["redis"])
            await self.short_term.initialize()
            
        # Initialize long-term memory (Postgres)
        if "postgres" in memory_config:
            from .memory.postgres_memory import PostgresMemory
            self.long_term = PostgresMemory(**memory_config["postgres"])
            await self.long_term.initialize()
        
        # Initialize model
        model_config = self.config.get("model_config", {})
        if not model_config.get("model_type"):
            raise ValueError("model_type is required in model_config")
            
        self.model = ModelFactory.create_model(**model_config)
    
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any] = None,
        use_long_term: bool = False
    ) -> str:
        """
        Process a user query.
        
        Args:
            query: User query
            context: Optional context
            use_long_term: Whether to use long-term memory
            
        Returns:
            Generated response
        """
        try:
            # Get memory context
            memory = self.long_term if use_long_term else self.short_term
            if not memory:
                raise RuntimeError("Memory system not initialized")
                
            # Retrieve context from memory
            memory_context = await memory.retrieve_context(query)
            
            # Combine contexts
            full_context = {**(context or {}), **memory_context}
            
            # Add tools context
            tools_context = {
                "available_tools": self.tools.get_tools_description()
            }
            full_context.update(tools_context)
            
            # Generate response with tool support
            response = await self.model.generate_response(
                query, 
                full_context,
                tools=self.tools  # Pass tools manager for execution
            )
            
            # Store interaction
            await memory.store_interaction(
                query=query,
                response=response,
                context=full_context
            )
            
            return response
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    async def close(self) -> None:
        """Clean up resources."""
        if self.short_term:
            await self.short_term.close()
        if self.long_term:
            await self.long_term.close()
        if self.model:
            await self.model.close() 