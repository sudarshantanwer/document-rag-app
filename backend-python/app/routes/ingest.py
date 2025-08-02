from fastapi import APIRouter, UploadFile, File
from app.services.ingest_service import ingest_document

router = APIRouter(prefix="/ingest")

@router.post("")
async def ingest(file: UploadFile = File(...)):
    return await ingest_document(file)
