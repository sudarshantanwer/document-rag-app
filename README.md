# Document RAG Application

A full-stack Retrieval-Augmented Generation (RAG) application that allows users to upload documents and query them using natural language. The system processes documents, creates embeddings, and uses AI to provide intelligent answers based on the document content.

![Project Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-19.1+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue)

## 🚀 Features

### 📄 Document Processing
- **Multi-format Support**: Upload PDF, TXT, and DOCX files
- **Intelligent Chunking**: Automatic text segmentation for optimal retrieval
- **Metadata Extraction**: Document information and chunk metadata storage

### 🤖 AI-Powered Querying
- **Natural Language Queries**: Ask questions in plain English
- **Context-Aware Responses**: AI provides answers based on document content
- **Source Attribution**: Responses include relevant document context

### 🔧 Performance & Reliability
- **Rate Limiting**: Configurable API rate limiting with Redis backing
- **Async Processing**: High-performance async operations
- **Retry Logic**: Automatic retry with exponential backoff
- **Health Monitoring**: Comprehensive health checks and performance metrics
- **CORS Support**: Cross-origin resource sharing configuration

### 🏗️ Production Ready
- **Docker Support**: Complete containerization with Docker Compose
- **Environment Configuration**: Flexible configuration management
- **Database Migrations**: Automatic table creation and schema management
- **Security Middleware**: Trusted host validation and security headers

## 🏛️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  React Frontend │◄──►│ FastAPI Backend │◄──►│ PostgreSQL+     │
│                 │    │                 │    │ pgvector        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────▼────┐             ┌────▼────┐             ┌────▼────┐
    │ Vite    │             │ Uvicorn │             │ Vector  │
    │ Dev     │             │ ASGI    │             │ Search  │
    │ Server  │             │ Server  │             │ Engine  │
    └─────────┘             └─────────┘             └─────────┘
```

### Tech Stack

**Frontend:**
- React 19.1+ with hooks
- Vite for build tooling
- TailwindCSS for styling
- Jest for testing

**Backend:**
- FastAPI with async/await
- SQLAlchemy with async support
- Pydantic for data validation
- LangChain for RAG implementation
- OpenAI/HuggingFace for embeddings

**Database:**
- PostgreSQL 16+ with pgvector extension
- Vector similarity search
- Document metadata storage

**Infrastructure:**
- Docker & Docker Compose
- Redis for rate limiting (optional)
- Nginx for production deployment

## 🚦 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/sudarshantanwer/document-rag-app.git
cd document-rag-app
```

### 2. Environment Setup
```bash
# Copy environment template
cp example.env .env

# Edit .env with your configuration
# Required: OPENAI_API_KEY
# Optional: REDIS_URL for enhanced rate limiting
```

### 3. Start with Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Manual Setup (Development)

#### Backend Setup
```bash
cd backend-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For production features (Redis, enhanced rate limiting)
pip install -r requirements-prod.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend-react

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

#### Database Setup
```bash
# Start PostgreSQL with pgvector
docker run -d \
  --name postgres-rag \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

## 📖 API Documentation

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns service health status and performance metrics.

#### Document Ingestion
```http
POST /ingest
Content-Type: multipart/form-data

file: <document.pdf|txt|docx>
```

#### Query Documents
```http
POST /query
Content-Type: application/json

{
  "question": "What is this document about?",
  "doc_id": "optional-document-id"
}
```

#### List Documents
```http
GET /documents
```

#### Select Documents for RAG
```http
POST /select-docs
Content-Type: application/json

{
  "doc_ids": ["doc-id-1", "doc-id-2"]
}
```

### Response Examples

**Successful Query Response:**
```json
{
  "answer": "This document is about...",
  "context": "Relevant document excerpts..."
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend-python

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health_endpoint.py -v
```

### Frontend Tests
```bash
cd frontend-react

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Current Test Status
- ✅ Health endpoint: 100% passing
- ✅ Performance middleware: 100% passing  
- ✅ Document selection: 100% passing
- ✅ Async optimization utils: 100% passing
- ⚠️ Query/Ingest services: Require database setup

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | - | Yes |
| `REDIS_URL` | Redis connection for rate limiting | `redis://localhost:6379` | No |
| `ENABLE_RATE_LIMITING` | Enable/disable rate limiting | `true` | No |
| `MAX_CONCURRENT_REQUESTS` | Max concurrent requests | `20` | No |
| `QUERY_RATE_LIMIT` | Queries per minute | `10` | No |
| `INGEST_RATE_LIMIT` | Ingests per 5 minutes | `5` | No |

### Performance Tuning

**Rate Limits (per IP):**
- Query: 10 requests/minute
- Ingest: 5 requests/5 minutes  
- Health: 60 requests/minute

**Timeouts:**
- Query: 25 seconds
- Ingest: 60 seconds
- Default: 30 seconds

**Concurrency:**
- Max concurrent requests: 20
- Query operations: 5 concurrent
- Ingest operations: 3 concurrent

## 🚀 Deployment

### Production Docker Build
```bash
# Build with production features
docker build --build-arg INSTALL_PROD=true -t document-rag-backend-prod ./backend-python

# Run with production settings
docker run -p 8000:8000 \
  -e DATABASE_URL="your-db-url" \
  -e OPENAI_API_KEY="your-api-key" \
  -e REDIS_URL="your-redis-url" \
  document-rag-backend-prod
```

### Production Checklist
- [ ] Set strong database passwords
- [ ] Configure proper CORS origins
- [ ] Set up Redis for rate limiting
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificates
- [ ] Configure log aggregation
- [ ] Set up health monitoring
- [ ] Configure backup strategy

## 🛠️ Development

### Project Structure
```
document-rag-app/
├── backend-python/           # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application entry point
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── db/              # Database models & sessions
│   │   ├── middleware/      # Performance & security middleware
│   │   └── utils/           # Utility functions
│   ├── tests/               # Test suite
│   ├── requirements.txt     # Basic dependencies
│   ├── requirements-prod.txt # Production dependencies
│   └── Dockerfile
├── frontend-react/          # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main component
│   │   ├── api.js          # API client
│   │   └── assets/         # Static assets
│   ├── public/             # Public assets
│   └── package.json
├── docker-compose.yml      # Multi-service orchestration
└── README.md              # This file
```

### Adding New Features

1. **Backend Endpoint:**
   ```python
   # app/routes/new_feature.py
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/new-feature")
   
   @router.post("")
   async def new_endpoint():
       return {"message": "Hello World"}
   ```

2. **Frontend Integration:**
   ```javascript
   // src/api.js
   export const newFeatureApi = async (data) => {
     const response = await fetch('/api/new-feature', {
       method: 'POST',
       body: JSON.stringify(data)
     });
     return response.json();
   };
   ```

### Performance Optimization

The application includes several performance optimizations:

- **Async Processing**: All I/O operations use async/await
- **Connection Pooling**: Database connections are pooled
- **Request Caching**: Responses cached with configurable TTL
- **Rate Limiting**: Prevents API abuse
- **GZIP Compression**: Response compression for bandwidth optimization
- **Middleware Stack**: Performance monitoring and timeout handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8, use `black` for formatting
- **JavaScript**: Use Prettier, follow Airbnb style guide
- **Commits**: Use conventional commit format

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'slowapi'**
```bash
# Install production dependencies
pip install -r requirements-prod.txt
# Or run without enhanced rate limiting
pip install -r requirements.txt
```

**2. Database Connection Failed**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Verify connection string
echo $DATABASE_URL
```

**3. OpenAI API Errors**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check API quota and billing
```

**4. Rate Limiting Issues**
```bash
# Disable rate limiting for development
export ENABLE_RATE_LIMITING=false

# Or increase limits in .env file
```

### Performance Issues

**Slow Queries:**
- Check database indexes
- Monitor query performance in logs
- Consider pagination for large datasets

**High Memory Usage:**
- Adjust chunk size for document processing
- Monitor embeddings cache size
- Consider document size limits

### Getting Help

- 📧 **Issues**: [GitHub Issues](https://github.com/sudarshantanwer/document-rag-app/issues)
- 📖 **Documentation**: [API Docs](http://localhost:8000/docs)
- 🔧 **Development**: Check `TESTING_SUMMARY.md` for test results

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [LangChain](https://langchain.com/) for RAG implementation
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity search
- [React](https://react.dev/) for the frontend framework
- [OpenAI](https://openai.com/) for embeddings and language models

---

**Made with ❤️ by [Sudarshan Tanwer](https://github.com/sudarshantanwer)**