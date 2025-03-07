import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Asegurarse de que el directorio raíz del proyecto esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importar después de ajustar sys.path
from code_review_assistant.api import app
from code_review_assistant.main import CodeReviewAssistant

# Variable global para almacenar el asistente durante las pruebas
_test_assistant = None

@pytest.fixture(scope="session", autouse=True)
def initialize_assistant():
    """
    Fixture que inicializa el asistente una vez para toda la sesión de pruebas.
    El parámetro autouse=True hace que este fixture se ejecute automáticamente.
    """
    global _test_assistant
    
    # Crear e inicializar el asistente de forma síncrona
    async def _init_assistant():
        print("Initializing CodeReviewAssistant...")
        assistant = CodeReviewAssistant()
        await assistant.initialize()
        print("CodeReviewAssistant initialized successfully")
        return assistant
    
    # Ejecutar la inicialización asíncrona en un bucle de eventos
    loop = asyncio.get_event_loop()
    _test_assistant = loop.run_until_complete(_init_assistant())
    
    # Asignar el asistente a app.state
    print("Setting app.state.assistant...")
    app.state.assistant = _test_assistant
    print(f"app.state.assistant set: {app.state.assistant is not None}")
    
    yield
    
    # Limpiar después de todas las pruebas
    print("Cleaning up assistant...")
    if hasattr(app.state, "assistant"):
        del app.state.assistant
    
    # No necesitas declarar global de nuevo aquí, ya lo hiciste al principio
    _test_assistant = None
    print("Cleanup complete")

@pytest.fixture
def client():
    """Fixture que proporciona un cliente de prueba."""
    print("Creating test client...")
    with TestClient(app) as test_client:
        print("Test client created")
        yield test_client
        print("Test client closed") 