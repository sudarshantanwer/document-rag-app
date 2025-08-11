# Redis Caching Implementation

This document describes the Redis caching implementation for the Document RAG application.

## Overview

The caching system implements a multi-layer Redis cache to improve performance by caching:
- **Embeddings**: Text embeddings from HuggingFace/OpenAI models
- **Query Results**: Complete RAG query responses 
- **Similarity Search**: Vector similarity search results

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   FastAPI       │    │   Redis Cache   │
│   Request       │───▶│   Backend       │◄──▶│   Layer         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   + pgvector    │
                       └─────────────────┘
```

## Components

### 1. Cache Service (`app/services/cache_service.py`)

Central Redis caching service that provides:
- Connection management
- Key generation and hashing
- TTL (Time To Live) management
- Cache statistics
- Error handling and graceful degradation

### 2. Cached Embeddings (`app/utils/cached_embeddings.py`)

Wrapper around LangChain embeddings that:
- Intercepts embedding requests
- Checks Redis cache first
- Falls back to original embeddings on cache miss
- Caches new embeddings automatically

### 3. Enhanced Services

#### Query Service
- Caches complete query results by question + filters
- Caches similarity search results separately
- Implements cache-first strategy

#### Ingest Service  
- Uses cached embeddings during document processing
- Automatically caches chunk embeddings

## Cache Keys

The system uses structured cache keys with SHA256 hashes for consistency:

```
embedding:{hash}     - Individual text embeddings
query:{hash}         - Complete RAG query results  
similarity:{hash}    - Vector similarity search results
```

Hash includes:
- Text content
- Model name
- Parameters (doc_id, k, etc.)

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600  # Default TTL in seconds (1 hour)

# Feature Flags
ENABLE_CACHING=true
CACHE_EMBEDDINGS=true
CACHE_QUERIES=true
```

### Docker Compose

Redis is included in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## Performance Benefits

### Before Caching
- Every query requires new embeddings generation (~100-500ms)
- Vector similarity search on every request (~50-200ms)
- LLM inference on every request (~1-3s)
- **Total: ~1.5-4s per query**

### After Caching
- Embedding cache hit: ~1-5ms
- Query cache hit: ~1-5ms  
- Similarity search cache hit: ~1-5ms
- **Total: ~5-15ms for cached queries (99% reduction)**

### Expected Cache Hit Rates
- **Embeddings**: 70-90% (common phrases, repeated queries)
- **Similarity Search**: 60-80% (similar questions)
- **Complete Queries**: 40-60% (exact question matches)

## Cache Invalidation

### Automatic
- TTL-based expiration (default 1 hour)
- LRU eviction when memory limit reached

### Manual
- Document-specific invalidation when new content added
- Admin endpoint to clear entire cache
- Per-service cache clearing capabilities

## Monitoring

### Admin Endpoints

```bash
# Get cache statistics
GET /admin/cache/stats

# Clear all cache (use with caution!)
POST /admin/cache/clear
```

### Cache Statistics

```json
{
  "cache_stats": {
    "status": "connected",
    "used_memory": "1.5M", 
    "connected_clients": 2,
    "total_commands_processed": 1000,
    "keyspace_hits": 800,
    "keyspace_misses": 200,
    "hit_rate": "80.0%"
  }
}
```

## Error Handling

### Graceful Degradation
- System continues working if Redis is unavailable
- Cache misses fall back to original implementations
- Errors are logged but don't break functionality

### Connection Management
- Automatic reconnection attempts
- Health checks in application startup
- Proper cleanup on shutdown

## Testing

Comprehensive test suite covers:
- Cache hit/miss scenarios
- Error handling and fallbacks
- Key generation consistency
- Async/sync compatibility
- Performance benchmarks

Run tests:
```bash
cd backend-python
pytest tests/test_cache_service.py
pytest tests/test_cached_embeddings.py
```

## Production Considerations

### Memory Management
- Configure Redis maxmemory appropriately
- Use LRU eviction policy for automatic cleanup
- Monitor memory usage and hit rates

### Security
- Use Redis AUTH in production
- Configure Redis to only accept connections from backend
- Consider Redis over TLS for sensitive deployments

### Scaling
- Single Redis instance suitable for moderate loads
- Consider Redis Cluster for high-scale deployments
- Monitor connection pool usage

### Backup & Recovery
- Redis persistence enabled with appendonly
- Regular backup of Redis data volume
- Cache is performance layer - can be rebuilt if lost

## Future Enhancements

1. **Smart Cache Warming**: Pre-populate cache with common queries
2. **Cache Analytics**: Detailed metrics on cache effectiveness
3. **Dynamic TTL**: Adjust TTL based on content type and usage patterns
4. **Distributed Caching**: Multi-instance Redis setup for scaling
5. **Cache Compression**: Compress cached data to save memory
6. **Semantic Cache Invalidation**: Invalidate related queries when content changes

## Troubleshooting

### Common Issues

1. **Cache Not Working**
   - Check Redis connection: `docker logs <redis-container>`
   - Verify REDIS_URL environment variable
   - Check application logs for connection errors

2. **Low Hit Rates**
   - Verify TTL isn't too short
   - Check if keys are being generated consistently
   - Monitor for frequent cache evictions

3. **Memory Issues**
   - Increase Redis maxmemory limit
   - Check for memory leaks in cache usage
   - Consider shorter TTL for less important data

4. **Performance Not Improved**
   - Verify caching is enabled in environment
   - Check cache hit rates via admin endpoint
   - Profile application to identify bottlenecks
