

import logging
from fastapi import APIRouter, HTTPException
from app.services.select_docs_service import select_documents
from app.schemas import SelectDocsRequest, SelectDocsResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/select-docs")

@router.post("", response_model=SelectDocsResponse)
async def select_docs(payload: SelectDocsRequest):
    try:
        return await select_documents(payload.dict())
    except Exception as e:
        logger.error(f"Select docs failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
