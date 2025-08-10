

import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from app.services.query_service import query_documents
from app.schemas import QueryRequest, QueryResponse
from app.middleware.rate_limiting import rate_limit_check, RATE_LIMITS
from app.utils.async_optimization import async_retry, async_timeout

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])

async def query_rate_limit(request: Request):
    """Rate limiting dependency for query endpoints"""
    limits = RATE_LIMITS["query"]
    await rate_limit_check(request, limits["limit"], limits["window"])

@router.post("", response_model=QueryResponse, dependencies=[Depends(query_rate_limit)])
@async_timeout(25.0)  # 25 second timeout
@async_retry(max_retries=2, delay=1.0)
async def query(payload: QueryRequest, request: Request):
    """Query documents using RAG with rate limiting and optimization"""
    try:
        logger.info(f"Processing query from {request.client.host}: {payload.question[:100]}...")
        result = await query_documents(payload.model_dump())
        logger.info(f"Query completed successfully")
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
