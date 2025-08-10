import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_health_endpoint():
    """Test the health endpoint"""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["message"] == "FastAPI Document-RAG Backend is running"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_health_endpoint_performance():
    """Test health endpoint returns quickly"""
    import time
    
    client = TestClient(app)
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should respond in under 1 second
