from typing import Dict, Any, Optional
from .memory import BaseMemory, RedisMemory, PostgresMemory
from .model.factory import ModelFactory
from .tools import Tools
from .orchestration import Orchestration

class AgentRuntime:
    """
    Main runtime class for the AI Agent system.
    Manages the lifecycle of agent components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent runtime with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize memory systems
        memory_config = config.get("memory_config", {})
        self.short_term = RedisMemory(**memory_config.get("redis", {}))
        self.long_term = PostgresMemory(**memory_config.get("postgres", {}))
        self.memory = self.short_term  # Default to short-term memory
        
        # Initialize model
        model_config = config.get("model_config", {})
        model_config["model_type"] = config.get("model_type", "ollama")
        self.model = ModelFactory.create_model(**model_config)
        
        # Initialize tools
        tools_config = config.get("tools_config", {})
        self.tools = Tools(**tools_config)
        
        # Initialize orchestration
        self.orchestration = Orchestration()
    
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        use_long_term: bool = False
    ) -> str:
        """
        Process a user query through the agent system.
        
        Args:
            query: The user's input query
            context: Optional additional context
            use_long_term: Whether to use long-term memory
            
        Returns:
            str: The generated response
        """
        try:
            # Switch memory system if needed
            self.memory = self.long_term if use_long_term else self.short_term
            
            # Process through orchestration
            response = await self.orchestration.process_query(
                query=query,
                context=context or {},
                memory=self.memory,
                model=self.model,
                tools=self.tools
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            # TODO: Add proper logging
            print(error_msg)
            return error_msg
    
    async def initialize(self) -> None:
        """Initialize all components."""
        await self.short_term.initialize()
        await self.long_term.initialize()
    
    async def close(self) -> None:
        """Cleanup and close all components."""
        await self.short_term.close()
        await self.long_term.close() 