"""
Performance and Rate Limiting Configuration
"""
import os
from typing import Dict, Any

class PerformanceConfig:
    """Configuration for performance optimizations"""
    
    # Rate Limiting
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    
    # Request Timeouts
    DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", "30.0"))
    QUERY_TIMEOUT = float(os.getenv("QUERY_TIMEOUT", "25.0"))
    INGEST_TIMEOUT = float(os.getenv("INGEST_TIMEOUT", "60.0"))
    
    # Concurrency Limits
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "20"))
    MAX_QUERY_CONCURRENT = int(os.getenv("MAX_QUERY_CONCURRENT", "5"))
    MAX_INGEST_CONCURRENT = int(os.getenv("MAX_INGEST_CONCURRENT", "3"))
    
    # Thread Pool
    THREAD_POOL_SIZE = int(os.getenv("THREAD_POOL_SIZE", "4"))
    
    # Cache Settings
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    # Rate Limits (requests per time window)
    RATE_LIMITS: Dict[str, Dict[str, Any]] = {
        "query": {
            "limit": int(os.getenv("QUERY_RATE_LIMIT", "10")),
            "window": int(os.getenv("QUERY_RATE_WINDOW", "60"))  # seconds
        },
        "ingest": {
            "limit": int(os.getenv("INGEST_RATE_LIMIT", "5")),
            "window": int(os.getenv("INGEST_RATE_WINDOW", "300"))
        },
        "health": {
            "limit": int(os.getenv("HEALTH_RATE_LIMIT", "60")),
            "window": int(os.getenv("HEALTH_RATE_WINDOW", "60"))
        },
        "default": {
            "limit": int(os.getenv("DEFAULT_RATE_LIMIT", "100")),
            "window": int(os.getenv("DEFAULT_RATE_WINDOW", "60"))
        }
    }
    
    # Performance Monitoring
    ENABLE_PERFORMANCE_LOGGING = os.getenv("ENABLE_PERFORMANCE_LOGGING", "true").lower() == "true"
    SLOW_REQUEST_THRESHOLD = float(os.getenv("SLOW_REQUEST_THRESHOLD", "1.0"))  # seconds
    
    # GZIP Compression
    GZIP_MINIMUM_SIZE = int(os.getenv("GZIP_MINIMUM_SIZE", "1000"))  # bytes
    
    @classmethod
    def get_rate_limit(cls, endpoint: str) -> Dict[str, int]:
        """Get rate limit configuration for specific endpoint"""
        return cls.RATE_LIMITS.get(endpoint, cls.RATE_LIMITS["default"])

# Create global config instance
config = PerformanceConfig()
