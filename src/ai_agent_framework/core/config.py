import os
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    """Configuration management for the agent runtime."""
    
    @staticmethod
    def load_config(env_file: str = None) -> Dict[str, Any]:
        """
        Load configuration from environment variables and/or .env file.
        
        Args:
            env_file: Optional path to .env file
            
        Returns:
            Dict containing all configuration
        """
        # Load .env file if specified
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        return {
            "memory_config": {
                "redis": {
                    "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
                    "ttl": int(os.getenv("REDIS_TTL", "3600"))
                },
                "postgres": {
                    "url": os.getenv("POSTGRES_URL", "postgresql://localhost:5432/agent"),
                    "table_name": os.getenv("POSTGRES_TABLE", "interactions")
                }
            },
            "model_config": {
                "model_type": os.getenv("MODEL_TYPE", "ollama"),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "model": os.getenv("MODEL_NAME", "llama2")
            },
            "tools_config": {
                "enabled": os.getenv("TOOLS_ENABLED", "true").lower() == "true",
                "plugins_dir": os.getenv("PLUGINS_DIR", "plugins")
            }
        }
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """
        Validate configuration values.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If required configuration is missing
        """
        model_config = config.get("model_config", {})
        model_type = model_config.get("model_type")
        
        if not model_type:
            raise ValueError("MODEL_TYPE is required")
            
        if model_type == "openai" and not model_config.get("api_key"):
            raise ValueError("OPENAI_API_KEY is required for OpenAI models") 