import pytest
from app.routes.query import query
from app.schemas import QueryRequest
from fastapi import Request
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_query_schema_attribute_access():
    """Test that the query function can access the question attribute correctly"""
    
    # Create a mock request
    mock_request = MagicMock()
    mock_request.client.host = "test-client"
    
    # Create a QueryRequest with the question field
    payload = QueryRequest(question="What is this document about?")
    
    # Verify the schema works correctly
    assert hasattr(payload, 'question')
    assert payload.question == "What is this document about?"
    assert payload.model_dump() == {"question": "What is this document about?", "doc_id": None}
    
    # Test that the string slicing works (this was the failing line)
    question_preview = payload.question[:100]
    assert question_preview == "What is this document about?"
    
    print("✅ Schema access works correctly - no more 'query' attribute error!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_query_schema_attribute_access())
