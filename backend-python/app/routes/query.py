from fastapi import APIRouter
from app.services.query_service import query_documents

router = APIRouter(prefix="/query")

@router.post("")
async def query(payload: dict):
    return await query_documents(payload)
