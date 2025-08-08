

import logging
from fastapi import APIRouter, HTTPException
from app.services.query_service import query_documents
from app.schemas import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query")

@router.post("", response_model=QueryResponse)
async def query(payload: QueryRequest):
    try:
        return await query_documents(payload.dict())
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
