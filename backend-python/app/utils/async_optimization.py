import asyncio
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Awaitable
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class AsyncOptimizer:
    """Utilities for async optimization"""
    
    def __init__(self, max_workers: int = 4):
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.cache: Dict[str, Any] = {}
        self.cache_lock = asyncio.Lock()
    
    async def run_in_thread(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Run CPU-intensive function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
    
    async def cached_call(self, key: str, func: Callable[..., Awaitable[T]], 
                         *args, ttl: int = 300, **kwargs) -> T:
        """Cached async function call with TTL"""
        async with self.cache_lock:
            if key in self.cache:
                result, timestamp = self.cache[key]
                if asyncio.get_event_loop().time() - timestamp < ttl:
                    logger.debug(f"Cache hit for {key}")
                    return result
                else:
                    del self.cache[key]
        
        # Execute function
        result = await func(*args, **kwargs)
        
        async with self.cache_lock:
            self.cache[key] = (result, asyncio.get_event_loop().time())
        
        logger.debug(f"Cache miss for {key}")
        return result
    
    def batch_processor(self, batch_size: int = 10, timeout: float = 1.0):
        """Decorator for batching async operations"""
        def decorator(func: Callable):
            batch_queue = []
            batch_lock = asyncio.Lock()
            
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                async with batch_lock:
                    batch_queue.append((args, kwargs))
                    
                    if len(batch_queue) >= batch_size:
                        current_batch = batch_queue.copy()
                        batch_queue.clear()
                        
                        # Process batch
                        tasks = [func(*item[0], **item[1]) for item in current_batch]
                        return await asyncio.gather(*tasks)
                
                # Wait for timeout or batch to fill
                await asyncio.sleep(timeout)
                async with batch_lock:
                    if batch_queue:
                        current_batch = batch_queue.copy()
                        batch_queue.clear()
                        tasks = [func(*item[0], **item[1]) for item in current_batch]
                        results = await asyncio.gather(*tasks)
                        return results[0] if len(results) == 1 else results
            
            return wrapper
        return decorator

# Global optimizer instance
async_optimizer = AsyncOptimizer()

def async_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying async functions with exponential backoff"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {current_delay}s")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        return wrapper
    return decorator

def async_timeout(timeout: float):
    """Decorator for adding timeout to async functions"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout}s")
                raise
        return wrapper
    return decorator

async def gather_with_concurrency(coro_list: list, max_concurrency: int = 10):
    """Execute coroutines with limited concurrency"""
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def sem_coro(coro):
        async with semaphore:
            return await coro
    
    return await asyncio.gather(*[sem_coro(coro) for coro in coro_list])

class ConnectionPool:
    """Simple async connection pool"""
    
    def __init__(self, create_connection: Callable, max_size: int = 10):
        self.create_connection = create_connection
        self.max_size = max_size
        self.pool = asyncio.Queue(maxsize=max_size)
        self.current_size = 0
        self.lock = asyncio.Lock()
    
    async def get_connection(self):
        """Get connection from pool"""
        try:
            return self.pool.get_nowait()
        except asyncio.QueueEmpty:
            async with self.lock:
                if self.current_size < self.max_size:
                    self.current_size += 1
                    return await self.create_connection()
                else:
                    return await self.pool.get()
    
    async def return_connection(self, connection):
        """Return connection to pool"""
        try:
            self.pool.put_nowait(connection)
        except asyncio.QueueFull:
            # Pool is full, discard connection
            await self.close_connection(connection)
            async with self.lock:
                self.current_size -= 1
    
    async def close_connection(self, connection):
        """Close connection (override in subclass)"""
        if hasattr(connection, 'close'):
            await connection.close()
