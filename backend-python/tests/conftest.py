import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from io import BytesIO

from app.main import app
from app.db.models import Base
from app.db.session import async_session

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create database session for testing"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """Create test client without database initialization"""
    from unittest.mock import patch
    
    # Mock the startup event to avoid database connections
    with patch('app.main.startup_event'):
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls"""
    with patch('openai.ChatCompletion.create') as mock:
        mock.return_value = {
            "choices": [{
                "message": {
                    "content": "Test answer from OpenAI"
                }
            }]
        }
        yield mock


@pytest.fixture
def mock_huggingface_pipeline():
    """Mock HuggingFace pipeline and components"""
    with patch('transformers.pipeline') as mock_pipeline, \
         patch('langchain.llms.HuggingFacePipeline') as mock_hf_pipeline:
        
        # Mock the transformers pipeline
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.return_value = ["Test answer from HuggingFace"]
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Mock the LangChain HuggingFacePipeline
        mock_hf_instance = MagicMock()
        mock_hf_instance.return_value = "Test answer from HuggingFace"
        mock_hf_pipeline.return_value = mock_hf_instance
        
        yield {
            "pipeline": mock_pipeline,
            "hf_pipeline": mock_hf_pipeline,
            "instance": mock_hf_instance
        }


@pytest.fixture
def mock_pgvector():
    """Mock PGVector for both ingest and query services"""
    with patch('langchain.vectorstores.pgvector.PGVector') as mock_pg:
        # Configure mock vector store
        mock_vector_store = MagicMock()
        mock_pg.return_value = mock_vector_store
        
        # Configure methods
        mock_vector_store.add_texts.return_value = ["vector_1", "vector_2"]
        mock_vector_store.similarity_search.return_value = [
            MagicMock(page_content="Test content chunk 1", metadata={"document_id": "test-doc"}),
            MagicMock(page_content="Test content chunk 2", metadata={"document_id": "test-doc"})
        ]
        
        yield {
            "pgvector": mock_pg,
            "store": mock_vector_store
        }


@pytest.fixture
def mock_embeddings():
    """Mock embeddings for testing"""
    with patch('langchain.embeddings.OpenAIEmbeddings') as mock_openai, \
         patch('langchain.embeddings.HuggingFaceEmbeddings') as mock_hf:
        
        # Configure mock embeddings
        mock_embedding_instance = MagicMock()
        mock_embedding_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_embedding_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        
        mock_openai.return_value = mock_embedding_instance
        mock_hf.return_value = mock_embedding_instance
        
        yield {
            "openai": mock_openai,
            "huggingface": mock_hf,
            "instance": mock_embedding_instance
        }


@pytest.fixture
def mock_text_splitter():
    """Mock text splitter"""
    with patch('langchain.text_splitter.CharacterTextSplitter') as mock_splitter:
        mock_instance = MagicMock()
        mock_instance.split_text.return_value = ["chunk 1", "chunk 2"]
        mock_splitter.return_value = mock_instance
        yield mock_splitter


@pytest.fixture
def mock_pdf_reader():
    """Mock PDF reader"""
    with patch('PyPDF2.PdfReader') as mock_reader:
        # Mock a page with text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF content"
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_reader.return_value = mock_reader_instance
        
        yield mock_reader


@pytest.fixture
def sample_document_data():
    """Sample document data for testing"""
    return {
        "filename": "test_document.txt",
        "content": "This is a test document content for unit testing.",
        "vector_ids": ["vector_1", "vector_2"],
        "num_chunks": 2
    }


@pytest.fixture
def sample_query_data():
    """Sample query data for testing"""
    return {
        "question": "What is the main topic of this document?",
        "doc_id": None
    }


@pytest.fixture
def mock_uploadfile():
    """Create a mock UploadFile for testing"""
    def create_upload_file(filename="test.txt", content="Test file content"):
        mock_file = MagicMock()
        mock_file.filename = filename
        mock_file.read = AsyncMock(return_value=content.encode('utf-8'))
        return mock_file
    
    return create_upload_file


@pytest.fixture
def mock_async_session():
    """Mock async database session"""
    with patch('app.db.session.async_session') as mock_session:
        mock_session_instance = AsyncMock()
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__.return_value = mock_session_instance
        mock_session_context.__aexit__.return_value = None
        mock_session.return_value = mock_session_context
        
        # Mock begin context manager
        mock_begin_context = AsyncMock()
        mock_begin_context.__aenter__.return_value = None
        mock_begin_context.__aexit__.return_value = None
        mock_session_instance.begin.return_value = mock_begin_context
        
        yield mock_session_instance


# Environment variable mocks
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables"""
    env_vars = {
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
        "PGVECTOR_CONN": "postgresql+psycopg2://test:test@localhost:5432/test",
        "OPENAI_API_KEY": "test-openai-key",
        "HUGGINGFACEHUB_API_TOKEN": "test-hf-token"
    }
    
    with patch.dict(os.environ, env_vars):
        yield
