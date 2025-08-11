"""
Redis caching service for embeddings and query results
"""
import json
import hashlib
import logging
from typing import Optional, Any, List
import redis.asyncio as redis
import os
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for embeddings and query results"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.default_ttl = int(os.getenv("REDIS_TTL", "3600"))  # 1 hour default
        
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis for caching")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🔌 Disconnected from Redis")
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key from arguments"""
        # Create a string representation of all arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = "|".join(key_parts)
        
        # Create hash for consistent key length
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    
    async def get_embedding_cache(self, text: str, model_name: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_cache_key("embedding", text, model_name=model_name)
            cached_result = await self.redis_client.get(cache_key)
            
            if cached_result:
                logger.info(f"📦 Cache HIT for embedding: {cache_key[:20]}...")
                return json.loads(cached_result)
            else:
                logger.debug(f"📭 Cache MISS for embedding: {cache_key[:20]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error getting embedding from cache: {e}")
            return None
    
    async def set_embedding_cache(self, text: str, model_name: str, embedding: List[float], ttl: Optional[int] = None) -> bool:
        """Cache embedding for text"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_cache_key("embedding", text, model_name=model_name)
            cache_ttl = ttl or self.default_ttl
            
            await self.redis_client.setex(
                cache_key, 
                cache_ttl, 
                json.dumps(embedding)
            )
            logger.info(f"💾 Cached embedding: {cache_key[:20]}... (TTL: {cache_ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching embedding: {e}")
            return False
    
    async def get_query_cache(self, question: str, doc_id: Optional[str] = None, k: int = 10) -> Optional[dict]:
        """Get cached query result"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_cache_key("query", question, doc_id=doc_id, k=k)
            cached_result = await self.redis_client.get(cache_key)
            
            if cached_result:
                logger.info(f"📦 Cache HIT for query: {cache_key[:20]}...")
                return json.loads(cached_result)
            else:
                logger.debug(f"📭 Cache MISS for query: {cache_key[:20]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error getting query result from cache: {e}")
            return None
    
    async def set_query_cache(self, question: str, result: dict, doc_id: Optional[str] = None, k: int = 10, ttl: Optional[int] = None) -> bool:
        """Cache query result"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_cache_key("query", question, doc_id=doc_id, k=k)
            cache_ttl = ttl or self.default_ttl
            
            await self.redis_client.setex(
                cache_key, 
                cache_ttl, 
                json.dumps(result)
            )
            logger.info(f"💾 Cached query result: {cache_key[:20]}... (TTL: {cache_ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching query result: {e}")
            return False
    
    async def get_similarity_search_cache(self, question: str, doc_id: Optional[str] = None, k: int = 10) -> Optional[List[dict]]:
        """Get cached similarity search results"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_cache_key("similarity", question, doc_id=doc_id, k=k)
            cached_result = await self.redis_client.get(cache_key)
            
            if cached_result:
                logger.info(f"📦 Cache HIT for similarity search: {cache_key[:20]}...")
                return json.loads(cached_result)
            else:
                logger.debug(f"📭 Cache MISS for similarity search: {cache_key[:20]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error getting similarity search from cache: {e}")
            return None
    
    async def set_similarity_search_cache(self, question: str, docs: List[dict], doc_id: Optional[str] = None, k: int = 10, ttl: Optional[int] = None) -> bool:
        """Cache similarity search results"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_cache_key("similarity", question, doc_id=doc_id, k=k)
            cache_ttl = ttl or self.default_ttl
            
            # Serialize documents to cache-friendly format
            serializable_docs = []
            for doc in docs:
                if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                    serializable_docs.append({
                        'page_content': doc.page_content,
                        'metadata': doc.metadata
                    })
                else:
                    serializable_docs.append(doc)
            
            await self.redis_client.setex(
                cache_key, 
                cache_ttl, 
                json.dumps(serializable_docs)
            )
            logger.info(f"💾 Cached similarity search: {cache_key[:20]}... (TTL: {cache_ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching similarity search: {e}")
            return False
    
    async def invalidate_document_cache(self, doc_id: str):
        """Invalidate all cache entries related to a specific document"""
        if not self.redis_client:
            return
            
        try:
            # Find all keys that might be related to this document
            patterns = [
                f"query:*doc_id={doc_id}*",
                f"similarity:*doc_id={doc_id}*"
            ]
            
            for pattern in patterns:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"🗑️ Invalidated {len(keys)} cache entries for document {doc_id}")
                    
        except Exception as e:
            logger.error(f"Error invalidating document cache: {e}")
    
    async def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {"status": "disconnected"}
            
        try:
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0), 
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> str:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return "0.0%"
        return f"{(hits / total * 100):.1f}%"

# Global cache service instance
cache_service = CacheService()
