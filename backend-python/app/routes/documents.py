
import logging
from fastapi import APIRouter, HTTPException
from app.db.session import async_session
from app.db.models import Document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents")

@router.get("")
async def list_documents():
    try:
        async with async_session() as session:
            result = await session.execute(
                Document.__table__.select()
            )
            docs = result.fetchall()
            return {
                "documents": [
                    {"id": str(doc.id), "filename": doc.filename} for doc in docs
                ]
            }
    except Exception as e:
        logger.error(f"List documents failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
