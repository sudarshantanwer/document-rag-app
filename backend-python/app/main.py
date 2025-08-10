
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.select_docs import router as select_docs_router
from app.routes.documents import router as documents_router
from app.db.models import Base
from app.db.session import engine
from app.middleware.performance import PerformanceMiddleware, AsyncLimitMiddleware
from app.middleware.rate_limiting import redis_limiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting FastAPI Document-RAG Backend")
    
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables initialized")
    
    # Initialize Redis rate limiter
    await redis_limiter.connect()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FastAPI Document-RAG Backend")
    if redis_limiter.redis_client:
        await redis_limiter.redis_client.close()

app = FastAPI(
    title="Document-RAG API",
    description="FastAPI backend for document ingestion and RAG queries",
    version="1.0.0",
    lifespan=lifespan
)

# Security and Performance Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure properly in production
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(AsyncLimitMiddleware, max_concurrent=20)
app.add_middleware(PerformanceMiddleware, max_request_time=30.0)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Docker frontend
        "http://frontend:3000"    # Docker internal network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Rate limiting error handler
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("✅ SlowAPI rate limiting enabled")
except ImportError:
    logger.warning("⚠️ SlowAPI not available. Using custom rate limiting implementation.")
    # Set a dummy limiter for the app state
    app.state.limiter = None

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running"""
    return {
        "status": "healthy",
        "message": "FastAPI Document-RAG Backend is running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(select_docs_router)
app.include_router(documents_router)
