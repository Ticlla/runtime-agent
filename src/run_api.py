#!/usr/bin/env python3
"""
Script to start the Code Review Assistant REST API.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from code_review_assistant.config import load_config

def start_api():
    config = load_config()
    host = config.get("api", {}).get("host", "0.0.0.0")
    port = int(config.get("api", {}).get("port", 8000))
    
    print(f"Starting Code Review Assistant API on {host}:{port}")
    uvicorn.run("code_review_assistant.api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_api() 