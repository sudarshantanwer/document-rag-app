import asyncio
import time
import os
from typing import Dict, Optional
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)

# Try to import slowapi components, but make them optional
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    logger.warning("SlowAPI not available. Using custom rate limiting implementation only.")
    SLOWAPI_AVAILABLE = False
    # Create dummy classes for type hints
    class RateLimitExceeded(Exception):
        pass

# Try to import Redis, but make it optional
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available. Using in-memory rate limiting only.")
    REDIS_AVAILABLE = False

# In-memory rate limiter for development (replace with Redis for production)
class InMemoryRateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit"""
        async with self.lock:
            now = time.time()
            window_start = now - window
            
            # Clean old requests
            if key in self.requests:
                self.requests[key] = [
                    req_time for req_time in self.requests[key] 
                    if req_time > window_start
                ]
            else:
                self.requests[key] = []
            
            # Check limit
            if len(self.requests[key]) >= limit:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True

# Redis-based rate limiter for production
class RedisRateLimiter:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[object] = None
    
    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            logger.info("Redis not available. Skipping Redis connection.")
            return
            
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Connected to Redis for rate limiting")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Using in-memory rate limiter.")
            self.redis_client = None
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed using Redis sliding window"""
        if not self.redis_client or not REDIS_AVAILABLE:
            return True  # Fallback: allow all requests if Redis unavailable
        
        try:
            pipe = self.redis_client.pipeline()
            now = time.time()
            window_start = now - window
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current requests
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(now): now})
            # Set expiry
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            return current_requests < limit
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            return True  # Fallback: allow request if Redis fails

# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()
redis_limiter = RedisRateLimiter(os.getenv("REDIS_URL", "redis://localhost:6379"))

# SlowAPI limiter for decorator-based rate limiting (optional)
if SLOWAPI_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Try to get real IP from headers first (for proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    if hasattr(request, 'client') and request.client:
        return request.client.host
    
    return "unknown"

async def rate_limit_check(request: Request, limit: int = 100, window: int = 60):
    """Manual rate limit check"""
    client_ip = get_client_ip(request)
    key = f"rate_limit:{client_ip}"
    
    # Try Redis first, fallback to in-memory
    if redis_limiter.redis_client and REDIS_AVAILABLE:
        allowed = await redis_limiter.is_allowed(key, limit, window)
    else:
        allowed = await rate_limiter.is_allowed(key, limit, window)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {limit} requests per {window} seconds."
        )

# Different rate limits for different operations
RATE_LIMITS = {
    "query": {"limit": 10, "window": 60},      # 10 queries per minute
    "ingest": {"limit": 5, "window": 300},     # 5 ingests per 5 minutes
    "health": {"limit": 60, "window": 60},     # 60 health checks per minute
    "default": {"limit": 100, "window": 60}    # 100 requests per minute
}
