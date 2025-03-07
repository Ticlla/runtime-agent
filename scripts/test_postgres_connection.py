import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# Añadir el directorio src al path para poder importar el paquete
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_agent_framework.core.memory.postgres_memory import PostgresMemory

async def test_postgres_connection():
    """Script para probar la conexión y operaciones con PostgreSQL."""
    print("Iniciando prueba de conexión a PostgreSQL...")
    
    try:
        print("Configuración de conexión:")
        dsn = "postgresql://admin:admin123@localhost:5432/agent_memory"
        print(f"DSN: {dsn}")
        
        # Crear instancia de PostgresMemory
        memory = PostgresMemory(
            dsn=dsn,
            table_name="long_term_memory"
        )
        
        print("✅ Instancia de PostgresMemory creada")
        
        print("Intentando inicializar la base de datos...")
        await memory.initialize()
        print("✅ Base de datos inicializada")
        
        # Probar almacenamiento
        # Crear un vector de 1536 dimensiones
        embedding = [0.1] * 1536  # Crear una lista de 1536 elementos
        
        await memory.store_interaction(
            query="¿Está funcionando PostgreSQL?",
            response="¡Sí, está funcionando!",
            context={"test": True, "timestamp": datetime.now().isoformat()},
            embedding=embedding  # Pasar la lista directamente
        )
        print("✅ Interacción almacenada correctamente")
        
        # Probar recuperación
        context = await memory.retrieve_context(
            query="test",
            embedding=embedding  # También aquí pasamos la lista
        )
        print("\nContexto recuperado:")
        print("-" * 50)
        for interaction in context["recent_interactions"]:
            print(f"Query: {interaction['query']}")
            print(f"Response: {interaction['response']}")
            print(f"Context: {interaction['context']}")
            print(f"Timestamp: {datetime.fromisoformat(interaction['timestamp'])}")
            print("-" * 50)
        
        # Limpiar datos de prueba
        await memory.clear()
        print("✅ Datos de prueba limpiados")
        
        # Cerrar conexión
        await memory.close()
        print("✅ Conexión cerrada correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        print("Stack trace:")
        print(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_postgres_connection())
        if success:
            print("\n✨ Prueba completada exitosamente!")
        else:
            print("\n❌ La prueba falló")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error en el main: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1) 