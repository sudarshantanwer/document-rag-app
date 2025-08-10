import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
from app.services.ingest_service import ingest_document


@pytest.mark.asyncio
async def test_ingest_text_document(mock_async_session, mock_pgvector, mock_embeddings, mock_text_splitter, mock_uploadfile):
    """Test ingesting a text document"""
    # Create a mock file
    mock_file = mock_uploadfile("test.txt", "This is test content")
    
    # Mock Document model
    with patch('app.services.ingest_service.Document') as mock_doc_class:
        mock_doc = MagicMock()
        mock_doc.id = "test-uuid"
        mock_doc_class.return_value = mock_doc
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data="This is test content")), \
             patch('os.remove'), \
             patch('tempfile.NamedTemporaryFile') as mock_temp:
            
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.txt"
            
            result = await ingest_document(mock_file)
            
            assert result["status"] == "success"
            assert result["filename"] == "test.txt"
            assert result["chunks"] == 2


@pytest.mark.asyncio
async def test_ingest_pdf_document(mock_async_session, mock_pgvector, mock_embeddings, mock_text_splitter, mock_pdf_reader, mock_uploadfile):
    """Test ingesting a PDF document"""
    # Create a mock PDF file
    mock_file = mock_uploadfile("test.pdf", b"PDF content")
    
    # Mock Document model
    with patch('app.services.ingest_service.Document') as mock_doc_class:
        mock_doc = MagicMock()
        mock_doc.id = "test-uuid"
        mock_doc_class.return_value = mock_doc
        
        # Mock file operations
        with patch('os.remove'), \
             patch('tempfile.NamedTemporaryFile') as mock_temp:
            
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.pdf"
            
            result = await ingest_document(mock_file)
            
            assert result["status"] == "success"
            assert result["filename"] == "test.pdf"
            assert result["chunks"] == 2


@pytest.mark.asyncio
async def test_ingest_unsupported_file_type(mock_uploadfile):
    """Test ingesting an unsupported file type"""
    # Create a mock file with unsupported extension
    mock_file = mock_uploadfile("test.xyz", "Some content")
    
    with patch('os.remove'), \
         patch('tempfile.NamedTemporaryFile') as mock_temp:
        
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.xyz"
        
        result = await ingest_document(mock_file)
        
        assert result["status"] == "error"
        assert "Unsupported file type" in result["message"]


@pytest.mark.asyncio
async def test_ingest_document_with_chunks(mock_async_session, mock_pgvector, mock_embeddings, mock_text_splitter, mock_uploadfile):
    """Test that document is properly chunked"""
    # Create a mock file
    mock_file = mock_uploadfile("test.txt", "This is a longer test content that should be split into chunks")
    
    # Configure text splitter to return multiple chunks
    mock_text_splitter.return_value.split_text.return_value = [
        "chunk 1", "chunk 2", "chunk 3"
    ]
    
    # Mock Document model
    with patch('app.services.ingest_service.Document') as mock_doc_class:
        mock_doc = MagicMock()
        mock_doc.id = "test-uuid"
        mock_doc_class.return_value = mock_doc
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data="This is a longer test content")), \
             patch('os.remove'), \
             patch('tempfile.NamedTemporaryFile') as mock_temp:
            
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.txt"
            
            result = await ingest_document(mock_file)
            
            assert result["status"] == "success"
            assert result["chunks"] == 3


@pytest.mark.asyncio
async def test_ingest_document_stores_metadata(mock_async_session, mock_pgvector, mock_embeddings, mock_text_splitter, mock_uploadfile):
    """Test that document metadata is properly stored"""
    # Create a mock file
    mock_file = mock_uploadfile("metadata_test.txt", "Content for metadata test")
    
    # Mock Document model
    with patch('app.services.ingest_service.Document') as mock_doc_class:
        mock_doc = MagicMock()
        mock_doc.id = "metadata-test-uuid"
        mock_doc_class.return_value = mock_doc
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data="Content for metadata test")), \
             patch('os.remove'), \
             patch('tempfile.NamedTemporaryFile') as mock_temp:
            
            mock_temp.return_value.__enter__.return_value.name = "/tmp/metadata_test.txt"
            
            result = await ingest_document(mock_file)
            
            # Verify vector store was called with metadata
            mock_pgvector["store"].add_texts.assert_called_once()
            args, kwargs = mock_pgvector["store"].add_texts.call_args
            
            # Check that metadata was passed
            metadatas = kwargs.get('metadatas', [])
            assert len(metadatas) == 2  # Two chunks
            assert all(metadata["document_id"] == "metadata-test-uuid" for metadata in metadatas)


@pytest.mark.asyncio
async def test_ingest_document_validation(mock_uploadfile):
    """Test document validation during ingestion"""
    # Test with empty filename
    mock_file = mock_uploadfile("", "Content")
    
    with patch('tempfile.NamedTemporaryFile') as mock_temp:
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test"
        
        # This should still work as the suffix logic handles empty extensions
        result = await ingest_document(mock_file)
        # The function will treat it as unsupported type due to no extension
        assert result["status"] == "error"
