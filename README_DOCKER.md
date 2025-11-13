# Docker Setup Guide

This guide explains how to run the Execution Plane platform using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

1. **Clone the repository** (if you haven't already)
   ```bash
   git clone <repository-url>
   cd execution-plane
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file** with your configuration:
   ```bash
   # Required: LLM API Keys
   OPENAI_API_KEY=your_key_here
   # or
   ANTHROPIC_API_KEY=your_key_here
   # or
   GROQ_API_KEY=your_key_here
   
   # Optional: Other services
   MEM0_API_KEY=your_key_here
   LANGFUSE_PUBLIC_KEY=your_key_here
   LANGFUSE_SECRET_KEY=your_key_here
   ```

4. **Start all services**
   ```bash
   docker-compose up -d
   ```

5. **Check service status**
   ```bash
   docker-compose ps
   ```

6. **View logs**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

## Services

The Docker Compose setup includes:

- **PostgreSQL** (port 5432) - Main database
- **Redis** (port 6379) - Caching and message queue
- **Qdrant** (ports 6333, 6334) - Vector database for embeddings
- **Backend API** (port 8000) - FastAPI application
- **Celery Worker** - Async task processing
- **Frontend** (port 8080) - React application (nginx)

## Accessing the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Development Mode

For development with hot reload:

```bash
# Start only infrastructure services
docker-compose -f docker-compose.dev.yml up -d postgres redis qdrant

# Run backend locally (with hot reload)
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally (with hot reload)
cd frontend
npm run dev
```

## Environment Variables

### Required Variables

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` or `GROQ_API_KEY` - At least one LLM provider key

### Optional Variables

- `POSTGRES_USER` - PostgreSQL username (default: execution_plane)
- `POSTGRES_PASSWORD` - PostgreSQL password (default: execution_plane_pass)
- `POSTGRES_DB` - Database name (default: execution_plane)
- `SECRET_KEY` - Secret key for JWT tokens (change in production!)
- `MEM0_API_KEY` - Mem0 API key for memory functionality
- `LANGFUSE_PUBLIC_KEY` - Langfuse public key for observability
- `LANGFUSE_SECRET_KEY` - Langfuse secret key
- `LANGFUSE_HOST` - Langfuse host URL

### Port Configuration

- `BACKEND_PORT` - Backend API port (default: 8000)
- `FRONTEND_PORT` - Frontend port (default: 8080)
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `REDIS_PORT` - Redis port (default: 6379)
- `QDRANT_PORT` - Qdrant HTTP port (default: 6333)
- `QDRANT_GRPC_PORT` - Qdrant gRPC port (default: 6334)

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes data)
```bash
docker-compose down -v
```

### Rebuild services
```bash
docker-compose build --no-cache
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Execute commands in containers
```bash
# Backend shell
docker-compose exec backend bash

# Run migrations
docker-compose exec backend python migrations/add_tenant_isolation.py

# Database shell
docker-compose exec postgres psql -U execution_plane -d execution_plane
```

### Restart a specific service
```bash
docker-compose restart backend
docker-compose restart frontend
```

## Database Migrations

After first startup, run migrations:

```bash
docker-compose exec backend python migrations/add_tenant_isolation.py
```

## Troubleshooting

### Port already in use
If a port is already in use, either:
1. Stop the conflicting service
2. Change the port in `.env` file

### Services won't start
1. Check logs: `docker-compose logs`
2. Verify Docker has enough resources
3. Check disk space: `docker system df`
4. Verify environment variables in `.env`

### Database connection errors
1. Wait for PostgreSQL to be healthy: `docker-compose ps`
2. Check database credentials in `.env`
3. Verify network connectivity: `docker-compose exec backend ping postgres`

### Frontend can't connect to backend
1. Check CORS settings in `backend/core/config.py`
2. Verify `ALLOWED_ORIGINS` includes frontend URL
3. Check backend logs for CORS errors

### Out of memory
If services crash due to memory:
1. Increase Docker memory limit
2. Reduce Celery worker concurrency in `docker-compose.yml`
3. Use development mode for lighter resource usage

## Production Deployment

For production:

1. **Change default passwords** in `.env`
2. **Set strong SECRET_KEY**: Generate with `openssl rand -hex 32`
3. **Use environment-specific database credentials**
4. **Enable SSL/TLS** for frontend (update nginx.conf)
5. **Set up proper backup** for PostgreSQL volumes
6. **Configure monitoring** and alerting
7. **Use secrets management** (Docker secrets, Vault, etc.)

## Data Persistence

Data is persisted in Docker volumes:
- `postgres_data` - Database data
- `redis_data` - Redis data
- `qdrant_data` - Vector database data
- `backend_data` - Application data

To backup:
```bash
docker run --rm -v execution-plane_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

To restore:
```bash
docker run --rm -v execution-plane_postgres_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/postgres_backup.tar.gz"
```

## Network Configuration

All services are on the `execution-plane-network` bridge network. Services can communicate using service names:
- `postgres` - Database
- `redis` - Redis
- `qdrant` - Qdrant
- `backend` - Backend API
- `frontend` - Frontend
- `celery-worker` - Celery worker

## Health Checks

All services include health checks. Check status:
```bash
docker-compose ps
```

Healthy services show `(healthy)` status.

## Scaling

To scale Celery workers:
```bash
docker-compose up -d --scale celery-worker=3
```

## Cleanup

Remove all containers, networks, and volumes:
```bash
docker-compose down -v
docker system prune -a
```

⚠️ **Warning**: This deletes all data!

