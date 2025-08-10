import pytest
import asyncio
from app.utils.async_optimization import AsyncOptimizer, async_retry, async_timeout

@pytest.mark.asyncio
async def test_async_optimizer_basic():
    """Test basic AsyncOptimizer functionality"""
    optimizer = AsyncOptimizer(max_workers=2)
    
    # Test run_in_thread
    def cpu_bound_task(x):
        return x * 2
    
    result = await optimizer.run_in_thread(cpu_bound_task, 5)
    assert result == 10

@pytest.mark.asyncio 
async def test_async_retry_decorator():
    """Test async retry decorator"""
    call_count = 0
    
    @async_retry(max_retries=2, delay=0.01)
    async def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Temporary failure")
        return "success"
    
    result = await failing_function()
    assert result == "success"
    assert call_count == 2

@pytest.mark.asyncio
async def test_async_timeout_decorator():
    """Test async timeout decorator"""
    
    @async_timeout(0.1)  # 100ms timeout
    async def slow_function():
        await asyncio.sleep(0.5)  # Takes 500ms
        return "too slow"
    
    with pytest.raises(asyncio.TimeoutError):
        await slow_function()

@pytest.mark.asyncio
async def test_async_timeout_success():
    """Test async timeout decorator with fast function"""
    
    @async_timeout(0.1)  # 100ms timeout
    async def fast_function():
        await asyncio.sleep(0.01)  # Takes 10ms
        return "fast enough"
    
    result = await fast_function()
    assert result == "fast enough"
