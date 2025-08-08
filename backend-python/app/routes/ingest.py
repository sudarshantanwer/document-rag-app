

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingest_service import ingest_document
from app.schemas import IngestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest")

@router.post("", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    try:
        return await ingest_document(file)
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
