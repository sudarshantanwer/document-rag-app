import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
from app.services.query_service import query_documents


@pytest.mark.asyncio
async def test_query_documents_success(mock_pgvector, mock_embeddings, mock_huggingface_pipeline):
    """Test successful document querying"""
    query_payload = {
        "question": "What is the main topic?",
        "doc_id": None
    }
    
    result = await query_documents(query_payload)
    
    assert "answer" in result
    assert "context" in result
    assert result["answer"] == "Test answer from HuggingFace"


@pytest.mark.asyncio
async def test_query_documents_with_doc_id(mock_pgvector, mock_embeddings, mock_huggingface_pipeline):
    """Test querying with specific document ID"""
    query_payload = {
        "question": "What is in this specific document?",
        "doc_id": "test-doc-123"
    }
    
    result = await query_documents(query_payload)
    
    # Verify similarity search was called with filter
    mock_pgvector["store"].similarity_search.assert_called_once()
    args, kwargs = mock_pgvector["store"].similarity_search.call_args
    assert "metadata" in kwargs
    assert kwargs["metadata"]["document_id"] == "test-doc-123"
    
    assert "answer" in result
    assert "context" in result


@pytest.mark.asyncio
async def test_query_documents_no_question():
    """Test query with no question provided"""
    query_payload = {}
    
    result = await query_documents(query_payload)
    
    assert "error" in result
    assert result["error"] == "No question provided."


@pytest.mark.asyncio
async def test_query_documents_empty_question():
    """Test query with empty question"""
    query_payload = {"question": ""}
    
    result = await query_documents(query_payload)
    
    assert "error" in result
    assert result["error"] == "No question provided."


@pytest.mark.asyncio
async def test_query_documents_context_generation(mock_pgvector, mock_embeddings, mock_huggingface_pipeline):
    """Test that context is properly generated from search results"""
    # Configure mock to return specific content
    mock_doc1 = MagicMock()
    mock_doc1.page_content = "First chunk of content"
    mock_doc2 = MagicMock()
    mock_doc2.page_content = "Second chunk of content"
    
    mock_pgvector["store"].similarity_search.return_value = [mock_doc1, mock_doc2]
    
    query_payload = {
        "question": "Test question"
    }
    
    result = await query_documents(query_payload)
    
    assert result["context"] == "First chunk of content\nSecond chunk of content"


@pytest.mark.asyncio
async def test_query_documents_context_truncation(mock_pgvector, mock_embeddings, mock_huggingface_pipeline):
    """Test that long context is properly truncated"""
    # Create a very long piece of content
    long_content = " ".join(["word"] * 300)  # 300 words, should be truncated to 200
    
    mock_doc = MagicMock()
    mock_doc.page_content = long_content
    mock_pgvector["store"].similarity_search.return_value = [mock_doc]
    
    query_payload = {
        "question": "Test question"
    }
    
    result = await query_documents(query_payload)
    
    # Check that context was truncated to approximately 200 words
    context_words = result["context"].split()
    assert len(context_words) <= 200


@pytest.mark.asyncio
async def test_query_documents_llm_interaction(mock_pgvector, mock_embeddings, mock_huggingface_pipeline):
    """Test that LLM is properly called with formatted prompt"""
    query_payload = {
        "question": "What is the answer?"
    }
    
    result = await query_documents(query_payload)
    
    # Verify that HuggingFacePipeline was called
    mock_huggingface_pipeline["hf_pipeline"].assert_called_once()
    mock_huggingface_pipeline["instance"].assert_called_once()


@pytest.mark.asyncio
async def test_query_documents_environment_variable_check():
    """Test behavior when PGVECTOR_CONN is not set"""
    with patch.dict('os.environ', {}, clear=True):
        query_payload = {
            "question": "Test question"
        }
        
        result = await query_documents(query_payload)
        
        assert "error" in result
        assert result["error"] == "PGVECTOR_CONN environment variable not set."


@pytest.mark.asyncio
async def test_query_documents_multiple_filters(mock_pgvector, mock_embeddings, mock_huggingface_pipeline):
    """Test querying with document ID creates proper filter"""
    query_payload = {
        "question": "What is in this document?",
        "doc_id": "specific-doc-uuid"
    }
    
    result = await query_documents(query_payload)
    
    # Verify the filter was constructed correctly
    call_args = mock_pgvector["store"].similarity_search.call_args
    assert call_args[1]["metadata"]["document_id"] == "specific-doc-uuid"


@pytest.mark.asyncio
async def test_query_documents_empty_search_results(mock_pgvector, mock_embeddings, mock_huggingface_pipeline):
    """Test behavior when no documents are found"""
    # Configure mock to return empty results
    mock_pgvector["store"].similarity_search.return_value = []
    
    query_payload = {
        "question": "Question with no results"
    }
    
    result = await query_documents(query_payload)
    
    # Should still return an answer (empty context)
    assert "answer" in result
    assert result["context"] == ""
