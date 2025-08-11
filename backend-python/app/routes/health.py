from fastapi import APIRouter
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "document-rag-backend"}

@router.get("/cache/stats")
async def get_cache_stats():
    """Get Redis cache statistics"""
    stats = await cache_service.get_cache_stats()
    return {"cache_stats": stats}

@router.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries (use with caution!)"""
    try:
        if cache_service.redis_client:
            await cache_service.redis_client.flushdb()
            return {"status": "success", "message": "Cache cleared successfully"}
        else:
            return {"status": "error", "message": "Cache service not available"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to clear cache: {e}"}
