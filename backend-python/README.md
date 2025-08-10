# FastAPI Document-RAG Backend

This backend provides endpoints for document ingestion, querying with RAG, and document selection. It uses FastAPI, async SQLAlchemy, Langchain/LlamaIndex, pgvector, and python-dotenv.

## Features
- **POST /ingest**: Upload PDF/txt/docx, generate embeddings, store in PostgreSQL+pgvector
- **POST /query**: Ask questions, retrieve relevant docs, get LLM answer using RAG
- **POST /select-docs**: Specify docs for RAG process
- **GET /health**: Health check endpoint with performance metrics

## Performance Features 🚀
- **Rate Limiting**: Configurable limits per endpoint with Redis backing
- **Async Optimization**: Concurrent request handling with limits
- **Request Timeouts**: Automatic timeout handling for long-running requests
- **Performance Monitoring**: Request timing and slow query detection
- **Connection Pooling**: Efficient database connection management
- **Caching**: Response caching with configurable TTL
- **Retry Logic**: Automatic retry with exponential backoff
- **GZIP Compression**: Response compression for bandwidth optimization

## Tech Stack
- FastAPI
- async SQLAlchemy
- Langchain or LlamaIndex
- pgvector
- python-dotenv
- Redis (for rate limiting)
- SlowAPI (for advanced rate limiting)

## Performance Configuration

### Rate Limits (per IP)
- **Query**: 10 requests/minute
- **Ingest**: 5 requests/5 minutes  
- **Health**: 60 requests/minute
- **Default**: 100 requests/minute

### Concurrency Limits
- **Max concurrent requests**: 20
- **Query operations**: 5 concurrent
- **Ingest operations**: 3 concurrent

### Timeouts
- **Default**: 30 seconds
- **Query**: 25 seconds
- **Ingest**: 60 seconds

## Running Locally
1. Install dependencies: `pip install -r requirements.txt`
2. For enhanced performance features: `pip install -r requirements-prod.txt`
3. Set up Redis (optional): `docker run -d -p 6379:6379 redis:alpine`
4. Configure environment: Copy `performance.env` to `.env` and update values
5. Start server: `uvicorn app.main:app --reload`

## Docker Deployment

### Basic deployment (without enhanced rate limiting):
```bash
docker build -t document-rag-backend .
docker run -p 8000:8000 document-rag-backend
```

### Production deployment (with Redis and enhanced rate limiting):
```bash
docker build --build-arg INSTALL_PROD=true -t document-rag-backend-prod .
docker run -p 8000:8000 document-rag-backend-prod
```

## Environment Variables
See `performance.env` for all configurable performance settings.

### Optional Dependencies
- **slowapi**: Enhanced rate limiting with decorators
- **redis/aioredis**: Redis-backed rate limiting (recommended for production)
- **gunicorn**: Production ASGI server

## Production Recommendations
1. Use Redis for rate limiting: Set `REDIS_URL` 
2. Install production dependencies: `pip install -r requirements-prod.txt`
3. Enable all performance features: Set `ENABLE_RATE_LIMITING=true`
4. Adjust limits based on your infrastructure
5. Monitor slow requests: Set appropriate `SLOW_REQUEST_THRESHOLD`
6. Use proper `allowed_hosts` in TrustedHostMiddleware
7. Use gunicorn or similar ASGI server for production
