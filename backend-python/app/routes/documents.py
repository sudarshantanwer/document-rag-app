from fastapi import APIRouter
from app.db.session import async_session
from app.db.models import Document

router = APIRouter(prefix="/documents")

@router.get("")
async def list_documents():
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
