"""
Cached embeddings wrapper for LangChain embeddings
"""
import logging
from typing import List, Optional
from langchain_core.embeddings import Embeddings
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

class CachedEmbeddings(Embeddings):
    """Wrapper around LangChain embeddings that adds Redis caching"""
    
    def __init__(self, embeddings: Embeddings, model_name: str = "default"):
        self.embeddings = embeddings
        self.model_name = model_name
        
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents with caching"""
        if not texts:
            return []
            
        results = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cached_embedding = await cache_service.get_embedding_cache(text, self.model_name)
            if cached_embedding:
                results.append(cached_embedding)
            else:
                results.append(None)  # Placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            logger.info(f"🔄 Generating {len(uncached_texts)} new embeddings")
            try:
                if hasattr(self.embeddings, 'aembed_documents'):
                    new_embeddings = await self.embeddings.aembed_documents(uncached_texts)
                else:
                    # Fallback to sync method
                    new_embeddings = self.embeddings.embed_documents(uncached_texts)
            except Exception as e:
                logger.error(f"Error generating embeddings: {e}")
                # Return sync embeddings as fallback
                new_embeddings = self.embeddings.embed_documents(uncached_texts)
            
            # Cache new embeddings and update results
            for i, (text, embedding) in enumerate(zip(uncached_texts, new_embeddings)):
                await cache_service.set_embedding_cache(text, self.model_name, embedding)
                results[uncached_indices[i]] = embedding
        
        return results
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Sync version of embed_documents"""
        # For sync version, we'll skip caching to avoid blocking
        logger.warning("⚠️ Using sync embed_documents - caching skipped")
        return self.embeddings.embed_documents(texts)
    
    async def aembed_query(self, text: str) -> List[float]:
        """Embed a single query with caching"""
        # Check cache first
        try:
            cached_embedding = await cache_service.get_embedding_cache(text, self.model_name)
            if cached_embedding:
                return cached_embedding
        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")
        
        # Generate new embedding
        logger.info("🔄 Generating new query embedding")
        try:
            if hasattr(self.embeddings, 'aembed_query'):
                embedding = await self.embeddings.aembed_query(text)
            else:
                # Fallback to sync method
                embedding = self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            # Final fallback to sync method
            embedding = self.embeddings.embed_query(text)
        
        # Cache the result
        try:
            await cache_service.set_embedding_cache(text, self.model_name, embedding)
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")
            
        return embedding
    
    def embed_query(self, text: str) -> List[float]:
        """Sync version of embed_query"""
        # For sync version, we'll skip caching to avoid blocking
        logger.warning("⚠️ Using sync embed_query - caching skipped")
        return self.embeddings.embed_query(text)

def create_cached_embeddings(embeddings: Embeddings, model_name: str = "default") -> CachedEmbeddings:
    """Factory function to create cached embeddings wrapper"""
    return CachedEmbeddings(embeddings, model_name)
