from typing import Dict, Any, Optional, List
import asyncpg
import json
from datetime import datetime
from .base import BaseMemory

class PostgresMemory(BaseMemory):
    """PostgreSQL-based long-term memory implementation."""
    
    def __init__(
        self,
        dsn: str = "postgresql://user:password@localhost:5432/agent_memory",
        table_name: str = "long_term_memory"
    ):
        """
        Initialize PostgreSQL memory.
        
        Args:
            dsn: PostgreSQL connection string
            table_name: Name of the table to store memories
        """
        self.dsn = dsn
        self.table_name = table_name
        self.pool = None
        
    async def initialize(self):
        """Initialize the database connection and create table if not exists."""
        self.pool = await asyncpg.create_pool(self.dsn)
        
        async with self.pool.acquire() as conn:
            # Crear extensión vector si no existe
            await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
            
            # Crear tabla
            await conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    context JSONB,
                    embedding VECTOR(1536),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índice para búsqueda por similitud
            await conn.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_embedding 
                ON {self.table_name} 
                USING ivfflat (embedding vector_cosine_ops)
            ''')
    
    async def store_interaction(
        self,
        query: str,
        response: str,
        context: Optional[Dict] = None,
        embedding: Optional[List[float]] = None
    ) -> None:
        """Store an interaction in the database."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                f'''
                INSERT INTO {self.table_name} 
                (query, response, context, embedding) 
                VALUES ($1, $2, $3, $4)
                ''',
                query,
                response,
                json.dumps(context) if context else None,
                embedding
            )
    
    async def retrieve_context(
        self,
        query: str,
        embedding: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve relevant context based on query and embedding."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f'''
                SELECT 
                    query, 
                    response, 
                    context,
                    timestamp
                FROM {self.table_name}
                ORDER BY embedding <-> $1
                LIMIT $2
                ''',
                embedding, limit
            )
            
            interactions = []
            for row in rows:
                interactions.append({
                    "query": row['query'],
                    "response": row['response'],
                    "context": json.loads(row['context']) if row['context'] else {},
                    "timestamp": row['timestamp'].timestamp() if row['timestamp'] else None
                })
            
            return {
                "source": "postgres",
                "recent_interactions": interactions
            }
    
    async def clear(self) -> None:
        """Clear all data from the table."""
        async with self.pool.acquire() as conn:
            await conn.execute(f'TRUNCATE TABLE {self.table_name}')
    
    async def close(self) -> None:
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None 