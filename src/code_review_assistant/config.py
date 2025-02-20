from typing import Dict
import os
from dotenv import load_dotenv

def load_config() -> Dict:
    """Load configuration from environment variables."""
    load_dotenv()
    
    # Asegurarnos de que tenemos las variables necesarias
    model_type = os.getenv("MODEL_TYPE", "openai")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY no está configurada en el archivo .env")
    
    return {
        "database": {
            "url": f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
                   f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        },
        "redis": {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "password": os.getenv("REDIS_PASSWORD"),
            "ttl": int(os.getenv("REDIS_TTL", 3600))
        },
        "model": {
            "type": model_type,
            "api_key": api_key,
            "model": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
            "temperature": 0.7,
            "max_tokens": 500
        },
        "tools": {
            "enabled": os.getenv("TOOLS_ENABLED", "true").lower() == "true",
            "plugins_dir": os.getenv("PLUGINS_DIR", "plugins")
        }
    } 