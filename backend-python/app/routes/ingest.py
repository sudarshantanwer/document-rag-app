

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from app.services.ingest_service import ingest_document
from app.schemas import IngestResponse
from app.middleware.rate_limiting import rate_limit_check, RATE_LIMITS
from app.utils.async_optimization import async_retry, async_timeout

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["Ingest"])

async def ingest_rate_limit(request: Request):
    """Rate limiting dependency for ingest endpoints"""
    limits = RATE_LIMITS["ingest"]
    await rate_limit_check(request, limits["limit"], limits["window"])

@router.post("", response_model=IngestResponse, dependencies=[Depends(ingest_rate_limit)])
@async_timeout(60.0)  # 60 second timeout for file processing
@async_retry(max_retries=1, delay=2.0)
async def ingest(file: UploadFile = File(...), request: Request = None):
    """Ingest document with rate limiting and optimization"""
    try:
        logger.info(f"Processing file upload from {request.client.host}: {file.filename}")
        result = await ingest_document(file)
        logger.info(f"File ingestion completed: {file.filename}")
        return result
    except Exception as e:
        logger.error(f"Ingest failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
