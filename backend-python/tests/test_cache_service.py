"""
Tests for Redis caching service
"""
import pytest
import pytest_asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.cache_service import CacheService

@pytest.fixture
def cache_service():
    """Create a cache service instance for testing"""
    service = CacheService()
    # Mock the Redis client
    service.redis_client = AsyncMock()
    return service

@pytest.mark.asyncio
async def test_embedding_cache_hit(cache_service):
    """Test embedding cache hit"""
    # Mock cache hit
    test_embedding = [0.1, 0.2, 0.3]
    cache_service.redis_client.get.return_value = json.dumps(test_embedding)
    
    result = await cache_service.get_embedding_cache("test text", "test-model")
    
    assert result == test_embedding
    cache_service.redis_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_embedding_cache_miss(cache_service):
    """Test embedding cache miss"""
    # Mock cache miss
    cache_service.redis_client.get.return_value = None
    
    result = await cache_service.get_embedding_cache("test text", "test-model")
    
    assert result is None
    cache_service.redis_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_set_embedding_cache(cache_service):
    """Test setting embedding cache"""
    test_embedding = [0.1, 0.2, 0.3]
    cache_service.redis_client.setex.return_value = True
    
    result = await cache_service.set_embedding_cache("test text", "test-model", test_embedding)
    
    assert result is True
    cache_service.redis_client.setex.assert_called_once()

@pytest.mark.asyncio
async def test_query_cache_hit(cache_service):
    """Test query cache hit"""
    test_result = {"answer": "test answer", "context": "test context"}
    cache_service.redis_client.get.return_value = json.dumps(test_result)
    
    result = await cache_service.get_query_cache("test question")
    
    assert result == test_result
    cache_service.redis_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_query_cache_miss(cache_service):
    """Test query cache miss"""
    cache_service.redis_client.get.return_value = None
    
    result = await cache_service.get_query_cache("test question")
    
    assert result is None
    cache_service.redis_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_set_query_cache(cache_service):
    """Test setting query cache"""
    test_result = {"answer": "test answer", "context": "test context"}
    cache_service.redis_client.setex.return_value = True
    
    result = await cache_service.set_query_cache("test question", test_result)
    
    assert result is True
    cache_service.redis_client.setex.assert_called_once()

@pytest.mark.asyncio
async def test_similarity_search_cache(cache_service):
    """Test similarity search caching"""
    test_docs = [
        {"page_content": "content 1", "metadata": {"doc_id": "1"}},
        {"page_content": "content 2", "metadata": {"doc_id": "2"}}
    ]
    cache_service.redis_client.get.return_value = json.dumps(test_docs)
    
    result = await cache_service.get_similarity_search_cache("test question")
    
    assert result == test_docs
    cache_service.redis_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_cache_key_generation(cache_service):
    """Test cache key generation is consistent"""
    key1 = cache_service._generate_cache_key("test", "arg1", "arg2", param1="value1")
    key2 = cache_service._generate_cache_key("test", "arg1", "arg2", param1="value1")
    key3 = cache_service._generate_cache_key("test", "arg1", "arg2", param1="value2")
    
    assert key1 == key2  # Same inputs should generate same key
    assert key1 != key3  # Different inputs should generate different keys
    assert key1.startswith("test:")  # Should have correct prefix

@pytest.mark.asyncio
async def test_invalidate_document_cache(cache_service):
    """Test document cache invalidation"""
    cache_service.redis_client.keys.return_value = ["query:key1", "similarity:key2"]
    cache_service.redis_client.delete.return_value = 2
    
    await cache_service.invalidate_document_cache("test-doc-id")
    
    cache_service.redis_client.keys.assert_called()
    # Should be called twice - once for each pattern
    assert cache_service.redis_client.delete.call_count == 2

@pytest.mark.asyncio
async def test_cache_stats(cache_service):
    """Test cache statistics retrieval"""
    mock_info = {
        "used_memory_human": "1.5M",
        "connected_clients": 2,
        "total_commands_processed": 1000,
        "keyspace_hits": 800,
        "keyspace_misses": 200
    }
    cache_service.redis_client.info.return_value = mock_info
    
    stats = await cache_service.get_cache_stats()
    
    assert stats["status"] == "connected"
    assert stats["used_memory"] == "1.5M"
    assert stats["hit_rate"] == "80.0%"

@pytest.mark.asyncio
async def test_cache_disabled_graceful_handling():
    """Test that cache operations handle disabled Redis gracefully"""
    service = CacheService()
    service.redis_client = None
    
    # All cache operations should return None/False when Redis is disabled
    assert await service.get_embedding_cache("text", "model") is None
    assert await service.set_embedding_cache("text", "model", [0.1]) is False
    assert await service.get_query_cache("question") is None
    assert await service.set_query_cache("question", {}) is False

@pytest.mark.asyncio
async def test_cache_connection():
    """Test Redis connection establishment"""
    service = CacheService()
    
    with patch('redis.asyncio.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_from_url.return_value = mock_redis
        
        await service.connect()
        
        assert service.redis_client is not None
        mock_from_url.assert_called_once()
        mock_redis.ping.assert_called_once()

@pytest.mark.asyncio
async def test_cache_connection_failure():
    """Test Redis connection failure handling"""
    service = CacheService()
    
    with patch('redis.asyncio.from_url') as mock_from_url:
        mock_from_url.side_effect = Exception("Connection failed")
        
        await service.connect()
        
        assert service.redis_client is None
