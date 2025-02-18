docker run --name postgres-memory -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=agent_memory -p 5432:5432 -d ankane/pgvector && docker exec -it postgres-memory psql -U admin -d agent_memory -c "CREATE EXTENSION IF NOT EXISTS vector;"


docker run --name redis-memory -p 6379:6379 -d redis