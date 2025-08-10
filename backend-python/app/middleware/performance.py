import time
import asyncio
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware:
    """Middleware for performance monitoring and optimization"""
    
    def __init__(self, app, max_request_time: float = 30.0):
        self.app = app
        self.max_request_time = max_request_time
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        request = Request(scope, receive)
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                message["headers"].append([
                    b"x-process-time", 
                    str(process_time).encode()
                ])
                
                # Log slow requests
                if process_time > 1.0:
                    logger.warning(
                        f"Slow request: {request.method} {request.url.path} "
                        f"took {process_time:.2f}s"
                    )
            
            await send(message)
        
        try:
            # Set timeout for requests
            await asyncio.wait_for(
                self.app(scope, receive, send_wrapper),
                timeout=self.max_request_time
            )
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {request.method} {request.url.path}")
            response = JSONResponse(
                status_code=408,
                content={"detail": "Request timeout"}
            )
            await response(scope, receive, send)


class AsyncLimitMiddleware:
    """Middleware to limit concurrent requests per endpoint"""
    
    def __init__(self, app, max_concurrent: int = 10):
        self.app = app
        self.max_concurrent = max_concurrent
        self.semaphores = {}
    
    def get_semaphore(self, path: str) -> asyncio.Semaphore:
        """Get or create semaphore for endpoint"""
        if path not in self.semaphores:
            # Different limits for different endpoints
            if path.startswith("/query"):
                limit = 5  # Lower limit for expensive query operations
            elif path.startswith("/ingest"):
                limit = 3  # Even lower for file processing
            else:
                limit = self.max_concurrent
            
            self.semaphores[path] = asyncio.Semaphore(limit)
        
        return self.semaphores[path]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        path = request.url.path
        semaphore = self.get_semaphore(path)
        
        if semaphore.locked():
            logger.warning(f"Rate limiting {path} - too many concurrent requests")
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many concurrent requests"}
            )
            await response(scope, receive, send)
            return
        
        async with semaphore:
            await self.app(scope, receive, send)
