from typing import Dict, Any, Optional
from .memory import BaseMemory
from .model.factory import ModelFactory
from .tools.tools_manager import ToolsManager
import json

class AgentRuntime:
    """Runtime environment for AI agents."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize runtime with configuration."""
        self.config = config
        self.model = None  # LLM (OpenAI, Ollama, etc)
        self.tools = ToolsManager()  # Herramientas disponibles
        self.short_term = None  # Memoria a corto plazo (Redis)
        self.long_term = None  # Memoria a largo plazo (Postgres)

    async def initialize(self) -> None:
        """Initialize agent runtime."""
        try:
            # Obtener la configuración del modelo
            model_config = self.config.get("model")
            if not model_config:
                raise ValueError("Model configuration is missing")
            
            # Crear instancia del modelo
            self.model = ModelFactory.create_model(model_config)
            
            # Inicializar memoria si está configurada
            if self.config.get("memory_config"):
                # 1. Inicializar sistemas de memoria
                memory_config = self.config.get("memory_config", {})
                
                # Redis para memoria a corto plazo
                if "redis" in memory_config:
                    from .memory.redis_memory import RedisMemory
                    self.short_term = RedisMemory(**memory_config["redis"])
                    await self.short_term.initialize()
                    
                # Postgres para memoria a largo plazo
                if "postgres" in memory_config:
                    from .memory.postgres_memory import PostgresMemory
                    self.long_term = PostgresMemory(**memory_config["postgres"])
                    await self.long_term.initialize()
            
        except Exception as e:
            print(f"Runtime Error: {str(e)}")

    async def process_query(
        self,
        query: str,
        context: Dict[str, Any] = None,
        use_long_term: bool = False
    ) -> str:
        """Process a user query with memory context and synthesize results."""
        try:
            # Inicializar contextos vacíos si no hay memoria
            memory_context = {}
            full_context = {**(context or {})}
            
            # Si hay sistema de memoria, usarlo
            if self.short_term or self.long_term:
                memory = self.long_term if use_long_term else self.short_term
                if memory:
                    memory_context = await memory.retrieve_context(query)
                    full_context.update(memory_context)
            
            # No ejecutar herramientas aquí - usar los resultados del contexto
            tools_results = full_context.get("analysis_results", {})
            
            # 5. Preparar prompt para síntesis
            synthesis_prompt = f"""
            You are an AI code review assistant. Analyze the code review results and provide a comprehensive synthesis.

            Code Review Results:
            {json.dumps(tools_results, indent=2)}

            Provide a comprehensive synthesis in this JSON format:
            {{
                "synthesis": {{
                    "key_findings": [
                        {{
                            "category": "code quality|security|performance|style",
                            "description": "detailed description",
                            "severity": "high|medium|low"
                        }}
                    ],
                    "patterns": [
                        {{
                            "type": "pattern type",
                            "description": "pattern description",
                            "impact": "impact description"
                        }}
                    ],
                    "insights": [
                        {{
                            "area": "improvement area",
                            "description": "detailed insight",
                            "action_items": ["suggested actions"]
                        }}
                    ],
                    "summary": "brief executive summary of the code quality"
                }},
                "metadata": {{
                    "tools_used": {json.dumps(list(tools_results.keys()))},
                    "confidence_score": "0.0 to 1.0"
                }}
            }}
            """
            
            # 6. Generar síntesis usando LLM
            synthesis = await self.model.generate_response(
                query=synthesis_prompt,
                context={
                    "task": "code_review_synthesis",
                    "tools_available": list(tools_results.keys())
                }
            )
            
            # Almacenar interacción solo si hay memoria
            if self.short_term or self.long_term:
                memory = self.long_term if use_long_term else self.short_term
                if memory:
                    try:
                        await memory.store_interaction(
                            query=query,
                            response=str(synthesis),
                            context=full_context
                        )
                    except Exception as e:
                        print(f"Warning: Failed to store in {memory.__class__.__name__}: {e}")
            
            return synthesis
            
        except Exception as e:
            print(f"Runtime Error: {str(e)}")
            return {
                "error": "synthesis_error",
                "message": str(e),
                "partial_results": {
                    "tools": tools_results if 'tools_results' in locals() else {},
                    "context": full_context if 'full_context' in locals() else {}
                }
            }
    
    async def close(self) -> None:
        """Clean up resources."""
        if self.short_term:
            await self.short_term.close()
        if self.long_term:
            await self.long_term.close()
        if self.model:
            await self.model.close() 