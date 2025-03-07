import asyncio
import sys
import os

# Añadir el directorio src al path para poder importar el paquete
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_agent_framework.core.memory.redis_memory import RedisMemory

async def test_redis_connection():
    """Script para probar la conexión y operaciones con Redis."""
    print("Iniciando prueba de conexión a Redis...")
    
    try:
        # Crear instancia de RedisMemory
        memory = RedisMemory(
            url="redis://localhost:6379",  # Usar el argumento 'url' según la definición de la clase
            ttl=3600
        )
        
        await memory.initialize()  # Asegúrate de inicializar la conexión
        
        print("✅ Instancia de RedisMemory creada")
        
        # Probar almacenamiento
        await memory.store_interaction(
            query="¿Está funcionando Redis?",
            response="¡Sí, está funcionando!",
            context={"test": True}
        )
        print("✅ Interacción almacenada correctamente")
        
        # Probar recuperación
        context = await memory.retrieve_context("test")
        print("\nContexto recuperado:")
        print("-" * 50)
        for interaction in context["recent_interactions"]:
            print(f"Query: {interaction['query']}")
            print(f"Response: {interaction['response']}")
            print(f"Context: {interaction['context']}")
            print(f"Timestamp: {interaction['timestamp']}")
            print("-" * 50)
        
        # Limpiar datos de prueba
        await memory.clear()
        print("✅ Datos de prueba limpiados")
        
        # Cerrar conexión
        await memory.close()
        print("✅ Conexión cerrada correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_redis_connection())
    if success:
        print("\n✨ Prueba completada exitosamente!")
    else:
        print("\n❌ La prueba falló")
        sys.exit(1) 