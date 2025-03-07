from typing import Dict, Any
import os
from dotenv import load_dotenv
import json
import yaml

def load_config() -> Dict[str, Any]:
    """
    Load configuration from file or environment variables.
    Priority: 1. Environment variables, 2. config.yaml, 3. config.json, 4. Default values
    """
    config = {
        # Default configuration
        "debug": False,
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_origins": ["*"],
            "workers": 4
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "password": "",
            "db": 0
        },
        "database": {
            "url": "postgresql://postgres:postgres@localhost:5432/code_review"
        },
        "tools": {
            "code_analyzer": {
                "enabled": True,
                "timeout": 30
            },
            "style_checker": {
                "enabled": True,
                "timeout": 30
            },
            "security_scanner": {
                "enabled": True,
                "timeout": 30
            },
            "performance_analyzer": {
                "enabled": True,
                "timeout": 30
            }
        }
    }
    
    # Try to load from config.yaml
    yaml_path = os.environ.get("CONFIG_YAML_PATH", "config.yaml")
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    _deep_update(config, yaml_config)
        except Exception as e:
            print(f"Error loading config from {yaml_path}: {str(e)}")
    
    # Try to load from config.json
    json_path = os.environ.get("CONFIG_JSON_PATH", "config.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                json_config = json.load(f)
                if json_config:
                    _deep_update(config, json_config)
        except Exception as e:
            print(f"Error loading config from {json_path}: {str(e)}")
    
    # Override with environment variables
    if os.environ.get("DEBUG"):
        config["debug"] = os.environ.get("DEBUG").lower() in ("true", "1", "yes")
    
    # API config
    if os.environ.get("API_HOST"):
        config["api"]["host"] = os.environ.get("API_HOST")
    if os.environ.get("API_PORT"):
        config["api"]["port"] = int(os.environ.get("API_PORT"))
    if os.environ.get("API_CORS_ORIGINS"):
        config["api"]["cors_origins"] = os.environ.get("API_CORS_ORIGINS").split(",")
    if os.environ.get("API_WORKERS"):
        config["api"]["workers"] = int(os.environ.get("API_WORKERS"))
    
    # Redis config
    if os.environ.get("REDIS_HOST"):
        config["redis"]["host"] = os.environ.get("REDIS_HOST")
    if os.environ.get("REDIS_PORT"):
        config["redis"]["port"] = int(os.environ.get("REDIS_PORT"))
    if os.environ.get("REDIS_PASSWORD"):
        config["redis"]["password"] = os.environ.get("REDIS_PASSWORD")
    if os.environ.get("REDIS_DB"):
        config["redis"]["db"] = int(os.environ.get("REDIS_DB"))
    
    # Database config
    if os.environ.get("DATABASE_URL"):
        config["database"]["url"] = os.environ.get("DATABASE_URL")
    
    return config

def _deep_update(d: Dict, u: Dict) -> Dict:
    """Recursively update a dictionary with another."""
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _deep_update(d[k], v)
        else:
            d[k] = v
    return d

def validate_config(config: Dict) -> None:
    """Validate configuration values."""
    required_keys = ["model", "database", "redis"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}") 