import os
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from src.code_review_assistant.models.analysis_history import Base
from src.code_review_assistant.config import load_config

def init_database():
    """Initialize the database and create tables."""
    config = load_config()
    url = config["database"]["url"]
    
    # Crear la base de datos si no existe
    if not database_exists(url):
        create_database(url)
        print(f"Database created successfully!")
    
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_database() 