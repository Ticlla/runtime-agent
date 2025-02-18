from typing import Dict, Any, Optional
from .orchestration import Orchestration
from .memory import RedisMemory
from .model import ModelFactory
from .tools import Tools

class AgentRuntime:
    """
    Main runtime class for the AI Agent system.
    Manages the interaction between all components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent runtime with configuration.
        
        Args:
            config: Configuration dictionary for the agent
        """
        self.config = config
        self.orchestration = Orchestration()
        
        # Initialize memory system
        memory_config = config.get("memory_config", {})
        self.memory = RedisMemory(**memory_config)
        
        self.model = ModelFactory.create_model(
            model_type=config.get("model_type", "ollama"),
            **config.get("model_config", {})
        )
        self.tools = Tools()
        
    async def process_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Process a user query through the agent system.
        
        Args:
            query: The user's input query
            context: Optional additional context
            
        Returns:
            str: The generated response
        """
        try:
            # Initialize request context
            request_context = context or {}
            
            # Let orchestration handle the process
            response = await self.orchestration.process_query(
                query=query,
                context=request_context,
                memory=self.memory,
                model=self.model,
                tools=self.tools
            )
            
            return response
            
        except Exception as e:
            # Log the error and return a safe response
            # TODO: Implement proper error handling and logging
            return f"Error processing query: {str(e)}" 