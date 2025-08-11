"""
Tests for cached embeddings wrapper
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.utils.cached_embeddings import CachedEmbeddings, create_cached_embeddings

@pytest.fixture
def mock_base_embeddings():
    """Create mock base embeddings"""
    embeddings = MagicMock()
    embeddings.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
    embeddings.embed_query.return_value = [0.5, 0.6]
    return embeddings

@pytest.fixture
def mock_cache_service():
    """Mock the cache service"""
    with patch('app.utils.cached_embeddings.cache_service') as mock:
        # Make the cache service methods async mocks
        mock.get_embedding_cache = AsyncMock()
        mock.set_embedding_cache = AsyncMock()
        yield mock

@pytest.mark.asyncio
async def test_cached_embeddings_cache_hit(mock_base_embeddings, mock_cache_service):
    """Test cached embeddings with cache hit"""
    # Setup cache hit
    mock_cache_service.get_embedding_cache.return_value = [0.7, 0.8]
    
    cached_embeddings = CachedEmbeddings(mock_base_embeddings, "test-model")
    result = await cached_embeddings.aembed_query("test query")
    
    assert result == [0.7, 0.8]
    mock_cache_service.get_embedding_cache.assert_called_once()
    # Base embeddings should not be called on cache hit
    mock_base_embeddings.embed_query.assert_not_called()

@pytest.mark.asyncio
async def test_cached_embeddings_cache_miss(mock_base_embeddings, mock_cache_service):
    """Test cached embeddings with cache miss"""
    # Setup cache miss
    mock_cache_service.get_embedding_cache.return_value = None
    mock_cache_service.set_embedding_cache.return_value = True
    
    cached_embeddings = CachedEmbeddings(mock_base_embeddings, "test-model")
    result = await cached_embeddings.aembed_query("test query")
    
    assert result == [0.5, 0.6]  # From base embeddings
    mock_cache_service.get_embedding_cache.assert_called_once()
    mock_cache_service.set_embedding_cache.assert_called_once()
    mock_base_embeddings.embed_query.assert_called_once()

@pytest.mark.asyncio
async def test_cached_embeddings_documents_partial_cache(mock_base_embeddings, mock_cache_service):
    """Test cached embeddings for documents with partial cache hit"""
    # Setup partial cache hit - first text cached, second not
    def cache_side_effect(text, model):
        if text == "cached text":
            return [0.9, 1.0]
        return None
    
    mock_cache_service.get_embedding_cache.side_effect = cache_side_effect
    mock_cache_service.set_embedding_cache.return_value = True
    
    cached_embeddings = CachedEmbeddings(mock_base_embeddings, "test-model")
    result = await cached_embeddings.aembed_documents(["cached text", "new text"])
    
    # Should return cached result for first text, computed result for second
    assert len(result) == 2
    assert result[0] == [0.9, 1.0]  # Cached
    assert result[1] == [0.1, 0.2]  # From base embeddings (first in mock return)
    
    # Should only compute embeddings for uncached text
    mock_base_embeddings.embed_documents.assert_called_once_with(["new text"])

@pytest.mark.asyncio
async def test_cached_embeddings_sync_fallback(mock_base_embeddings, mock_cache_service):
    """Test that sync methods work without caching"""
    cached_embeddings = CachedEmbeddings(mock_base_embeddings, "test-model")
    
    # Test sync query
    result = cached_embeddings.embed_query("test query")
    assert result == [0.5, 0.6]
    mock_base_embeddings.embed_query.assert_called_once_with("test query")
    
    # Test sync documents
    result = cached_embeddings.embed_documents(["text1", "text2"])
    assert result == [[0.1, 0.2], [0.3, 0.4]]
    mock_base_embeddings.embed_documents.assert_called_once_with(["text1", "text2"])
    
    # Cache should not be used for sync methods
    mock_cache_service.get_embedding_cache.assert_not_called()

@pytest.mark.asyncio
async def test_cached_embeddings_async_base_embeddings(mock_cache_service):
    """Test with async base embeddings"""
    # Create async base embeddings
    async_embeddings = MagicMock()
    async_embeddings.aembed_query = AsyncMock(return_value=[0.7, 0.8])
    async_embeddings.aembed_documents = AsyncMock(return_value=[[0.1, 0.2]])
    
    # Setup cache miss
    mock_cache_service.get_embedding_cache.return_value = None
    mock_cache_service.set_embedding_cache.return_value = True
    
    cached_embeddings = CachedEmbeddings(async_embeddings, "test-model")
    
    # Test async query
    result = await cached_embeddings.aembed_query("test query")
    assert result == [0.7, 0.8]
    async_embeddings.aembed_query.assert_called_once_with("test query")
    
    # Test async documents
    result = await cached_embeddings.aembed_documents(["text1"])
    assert result == [[0.1, 0.2]]
    async_embeddings.aembed_documents.assert_called_once_with(["text1"])

def test_create_cached_embeddings_factory(mock_base_embeddings):
    """Test the factory function"""
    result = create_cached_embeddings(mock_base_embeddings, "test-model")
    
    assert isinstance(result, CachedEmbeddings)
    assert result.embeddings == mock_base_embeddings
    assert result.model_name == "test-model"

@pytest.mark.asyncio
async def test_cached_embeddings_error_handling(mock_base_embeddings, mock_cache_service):
    """Test error handling in cached embeddings"""
    # Setup cache service to raise exception
    mock_cache_service.get_embedding_cache.side_effect = Exception("Cache error")
    
    cached_embeddings = CachedEmbeddings(mock_base_embeddings, "test-model")
    
    # Should fall back to base embeddings when cache fails
    result = await cached_embeddings.aembed_query("test query")
    assert result == [0.5, 0.6]  # From base embeddings
    mock_base_embeddings.embed_query.assert_called_once()

@pytest.mark.asyncio
async def test_cached_embeddings_empty_documents(mock_base_embeddings, mock_cache_service):
    """Test cached embeddings with empty document list"""
    cached_embeddings = CachedEmbeddings(mock_base_embeddings, "test-model")
    
    result = await cached_embeddings.aembed_documents([])
    
    assert result == []
    # Should not call base embeddings for empty list
    mock_base_embeddings.embed_documents.assert_not_called()
    mock_cache_service.get_embedding_cache.assert_not_called()
