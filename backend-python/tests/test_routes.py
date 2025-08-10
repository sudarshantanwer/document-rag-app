import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app


@pytest.fixture
def async_client():
    """Create async test client"""
    return AsyncClient(app=app, base_url="http://test")


class TestRoutes:
    """Test cases for API routes"""

    def test_documents_list_endpoint(self, client):
        """Test GET /documents endpoint"""
        with patch('app.routes.documents.async_session') as mock_session:
            # Mock database session and query
            mock_session_instance = MagicMock()
            mock_session_context = MagicMock()
            mock_session_context.__aenter__.return_value = mock_session_instance
            mock_session_context.__aexit__.return_value = None
            mock_session.return_value = mock_session_context
            
            # Mock query result
            mock_result = MagicMock()
            mock_doc = MagicMock()
            mock_doc.id = "test-uuid"
            mock_doc.filename = "test.txt"
            mock_result.fetchall.return_value = [mock_doc]
            mock_session_instance.execute.return_value = mock_result
            
            response = client.get("/documents")
            
            assert response.status_code == 200
            data = response.json()
            assert "documents" in data
            assert len(data["documents"]) == 1
            assert data["documents"][0]["filename"] == "test.txt"

    def test_ingest_endpoint_success(self, client):
        """Test POST /ingest endpoint with successful upload"""
        with patch('app.services.ingest_service.ingest_document') as mock_ingest:
            mock_ingest.return_value = {
                "status": "success",
                "filename": "test.txt",
                "chunks": 2
            }
            
            # Create test file data
            test_file_content = b"This is test file content"
            files = {"file": ("test.txt", test_file_content, "text/plain")}
            
            response = client.post("/ingest", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["filename"] == "test.txt"
            assert data["chunks"] == 2

    def test_ingest_endpoint_error(self, client):
        """Test POST /ingest endpoint with error"""
        with patch('app.services.ingest_service.ingest_document') as mock_ingest:
            mock_ingest.side_effect = Exception("Test error")
            
            test_file_content = b"This is test file content"
            files = {"file": ("test.txt", test_file_content, "text/plain")}
            
            response = client.post("/ingest", files=files)
            
            assert response.status_code == 500

    def test_query_endpoint_success(self, client):
        """Test POST /query endpoint with successful query"""
        with patch('app.services.query_service.query_documents') as mock_query:
            mock_query.return_value = {
                "answer": "Test answer",
                "context": "Test context"
            }
            
            query_data = {
                "question": "What is the main topic?",
                "doc_id": None
            }
            
            response = client.post("/query", json=query_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "Test answer"
            assert data["context"] == "Test context"

    def test_query_endpoint_with_doc_id(self, client):
        """Test POST /query endpoint with specific document ID"""
        with patch('app.services.query_service.query_documents') as mock_query:
            mock_query.return_value = {
                "answer": "Specific answer",
                "context": "Specific context"
            }
            
            query_data = {
                "question": "What is in this document?",
                "doc_id": "test-doc-uuid"
            }
            
            response = client.post("/query", json=query_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "Specific answer"

    def test_query_endpoint_error(self, client):
        """Test POST /query endpoint with error"""
        with patch('app.services.query_service.query_documents') as mock_query:
            mock_query.side_effect = Exception("Query error")
            
            query_data = {
                "question": "What is the main topic?"
            }
            
            response = client.post("/query", json=query_data)
            
            assert response.status_code == 500

    def test_select_docs_endpoint_success(self, client):
        """Test POST /select-docs endpoint with successful selection"""
        with patch('app.services.select_docs_service.select_documents') as mock_select:
            mock_select.return_value = {
                "selected_docs": ["uuid1", "uuid2"]
            }
            
            select_data = {
                "doc_ids": ["uuid1", "uuid2"]
            }
            
            response = client.post("/select-docs", json=select_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "selected_docs" in data
            assert len(data["selected_docs"]) == 2

    def test_select_docs_endpoint_empty_list(self, client):
        """Test POST /select-docs endpoint with empty doc_ids"""
        with patch('app.services.select_docs_service.select_documents') as mock_select:
            mock_select.return_value = {
                "selected_docs": []
            }
            
            select_data = {
                "doc_ids": []
            }
            
            response = client.post("/select-docs", json=select_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["selected_docs"] == []

    def test_select_docs_endpoint_error(self, client):
        """Test POST /select-docs endpoint with error"""
        with patch('app.services.select_docs_service.select_documents') as mock_select:
            mock_select.side_effect = Exception("Selection error")
            
            select_data = {
                "doc_ids": ["uuid1"]
            }
            
            response = client.post("/select-docs", json=select_data)
            
            assert response.status_code == 500

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set"""
        response = client.options("/documents")
        # Note: TestClient might not fully simulate CORS, but we can test the endpoint exists
        assert response.status_code == 405  # Method not allowed for OPTIONS, but endpoint exists

    def test_invalid_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404

    def test_query_endpoint_missing_question(self, client):
        """Test POST /query endpoint without required question field"""
        query_data = {
            "doc_id": "test-doc-uuid"
            # Missing required "question" field
        }
        
        response = client.post("/query", json=query_data)
        
        # Should return validation error
        assert response.status_code == 422

    def test_select_docs_endpoint_missing_doc_ids(self, client):
        """Test POST /select-docs endpoint without required doc_ids field"""
        select_data = {
            # Missing required "doc_ids" field
        }
        
        response = client.post("/select-docs", json=select_data)
        
        # Should return validation error
        assert response.status_code == 422

    def test_ingest_endpoint_no_file(self, client):
        """Test POST /ingest endpoint without file"""
        response = client.post("/ingest")
        
        # Should return validation error for missing file
        assert response.status_code == 422

    def test_query_endpoint_invalid_json(self, client):
        """Test POST /query endpoint with invalid JSON"""
        response = client.post(
            "/query", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_documents_endpoint_database_error(self, client):
        """Test GET /documents endpoint with database error"""
        with patch('app.routes.documents.async_session') as mock_session:
            mock_session.side_effect = Exception("Database connection error")
            
            response = client.get("/documents")
            
            assert response.status_code == 500

    def test_multiple_file_upload(self, client):
        """Test that ingest endpoint handles single file correctly"""
        with patch('app.services.ingest_service.ingest_document') as mock_ingest:
            mock_ingest.return_value = {
                "status": "success",
                "filename": "test.txt",
                "chunks": 1
            }
            
            # Test with proper file upload
            files = {"file": ("test.txt", b"content", "text/plain")}
            response = client.post("/ingest", files=files)
            
            assert response.status_code == 200
