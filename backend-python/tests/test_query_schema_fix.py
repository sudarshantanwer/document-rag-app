import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_query_endpoint_schema_fix():
    """Test that the query endpoint correctly handles the 'question' field"""
    client = TestClient(app)
    
    # Test with correct schema
    response = client.post("/query", json={
        "question": "What is this document about?"
    })
    
    # The request should at least not fail with schema errors
    # It might fail with other errors (like missing OpenAI key) but not schema errors
    assert response.status_code != 422  # Unprocessable Entity (schema error)
    
    # Test with missing question field
    response = client.post("/query", json={})
    assert response.status_code == 422  # Should fail validation
    
    # Test with empty question
    response = client.post("/query", json={
        "question": ""
    })
    assert response.status_code != 422  # Should pass schema validation

def test_query_endpoint_with_doc_id():
    """Test query endpoint with optional doc_id"""
    client = TestClient(app)
    
    response = client.post("/query", json={
        "question": "What is this document about?",
        "doc_id": "some-uuid-here"
    })
    
    # Should not fail with schema errors
    assert response.status_code != 422
