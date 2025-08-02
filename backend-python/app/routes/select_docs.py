from fastapi import APIRouter
from app.services.select_docs_service import select_documents

router = APIRouter(prefix="/select-docs")

@router.post("")
async def select_docs(payload: dict):
    return await select_documents(payload)
