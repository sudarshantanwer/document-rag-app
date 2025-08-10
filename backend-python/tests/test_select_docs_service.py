import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.select_docs_service import select_documents


@pytest.mark.asyncio
async def test_select_documents_success(mock_async_session):
    """Test successful document selection - should return empty list when 'selected' field doesn't exist"""
    # Mock Document model without 'selected' field (current implementation)
    with patch('app.db.models.Document') as mock_doc_class:
        mock_doc = MagicMock()
        mock_doc.id = "test-uuid-1"
        # Don't add selected attribute to simulate real Document model

        # Mock session.get to return our mock document
        mock_async_session.get.return_value = mock_doc

        payload = {
            "doc_ids": ["550e8400-e29b-41d4-a716-446655440000"]
        }

        result = await select_documents(payload)

        # Should return empty list since Document model doesn't have 'selected' field
        assert result["selected_docs"] == []
@pytest.mark.asyncio
async def test_select_documents_no_doc_ids():
    """Test selection with no document IDs provided"""
    payload = {}
    
    result = await select_documents(payload)
    
    assert "error" in result
    assert result["error"] == "No doc_ids provided."


@pytest.mark.asyncio
async def test_select_documents_empty_doc_ids():
    """Test selection with empty document IDs list"""
    payload = {
        "doc_ids": []
    }
    
    result = await select_documents(payload)
    
    assert "error" in result
    assert result["error"] == "No doc_ids provided."


@pytest.mark.asyncio
async def test_select_documents_multiple_ids(mock_async_session):
    """Test selecting multiple documents - should return empty list when 'selected' field doesn't exist"""
    with patch('app.db.models.Document') as mock_doc_class:
        # Create mock documents without 'selected' field
        mock_doc1 = MagicMock()
        mock_doc1.id = "test-uuid-1"

        mock_doc2 = MagicMock()
        mock_doc2.id = "test-uuid-2"

        # Mock session.get to return documents based on call order
        mock_async_session.get.side_effect = [mock_doc1, mock_doc2]

        payload = {
            "doc_ids": [
                "550e8400-e29b-41d4-a716-446655440001",
                "550e8400-e29b-41d4-a716-446655440002"
            ]
        }

        result = await select_documents(payload)

        # Should return empty list since Document model doesn't have 'selected' field
        assert len(result["selected_docs"]) == 0


@pytest.mark.asyncio
async def test_select_documents_invalid_uuid(mock_async_session):
    """Test selection with invalid UUID format"""
    payload = {
        "doc_ids": ["invalid-uuid", "not-a-uuid"]
    }
    
    result = await select_documents(payload)
    
    # Should return empty list for invalid UUIDs
    assert result["selected_docs"] == []


@pytest.mark.asyncio
async def test_select_documents_nonexistent_document(mock_async_session):
    """Test selection of non-existent document"""
    # Mock session.get to return None (document not found)
    mock_async_session.get.return_value = None
    
    payload = {
        "doc_ids": ["550e8400-e29b-41d4-a716-446655440000"]
    }
    
    result = await select_documents(payload)
    
    # Should return empty list for non-existent documents
    assert result["selected_docs"] == []


@pytest.mark.asyncio
async def test_select_documents_without_selected_field(mock_async_session):
    """Test selection on documents without selected field"""
    with patch('app.db.models.Document') as mock_doc_class:
        mock_doc = MagicMock()
        mock_doc.id = "test-uuid-1"
        # Don't add selected attribute to simulate missing field
        
        mock_async_session.get.return_value = mock_doc
        
        payload = {
            "doc_ids": ["550e8400-e29b-41d4-a716-446655440000"]
        }
        
        result = await select_documents(payload)
        
        # Should skip documents without selected field
        assert result["selected_docs"] == []


@pytest.mark.asyncio
async def test_select_documents_mixed_valid_invalid(mock_async_session):
    """Test selection with mix of valid and invalid UUIDs"""
    with patch('app.db.models.Document') as mock_doc_class:
        mock_doc = MagicMock()
        mock_doc.id = "test-uuid-valid"
        # Don't add selected attribute to simulate real Document model

        # First call returns None (invalid), second returns doc
        mock_async_session.get.side_effect = [None, mock_doc]

        payload = {
            "doc_ids": [
                "invalid-uuid",
                "550e8400-e29b-41d4-a716-446655440000"
            ]
        }

        result = await select_documents(payload)

        # Should return empty list since Document model doesn't have 'selected' field
        assert len(result["selected_docs"]) == 0
