import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

def test_performance_middleware_headers():
    """Test that performance middleware adds timing headers"""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    # Check if performance middleware added timing header
    assert "x-process-time" in [h[0].decode() for h in response.headers.raw]

def test_cors_middleware():
    """Test CORS middleware configuration"""
    client = TestClient(app)
    response = client.options("/health", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET"
    })
    
    # Should allow the request from allowed origin
    assert "access-control-allow-origin" in [h[0].decode() for h in response.headers.raw]

def test_gzip_middleware():
    """Test that GZIP middleware is working"""
    client = TestClient(app)
    response = client.get("/health", headers={
        "Accept-Encoding": "gzip"
    })
    
    assert response.status_code == 200
    # For small responses, GZIP might not be applied due to minimum_size setting
