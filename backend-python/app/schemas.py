from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    question: str
    doc_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    context: Optional[str] = None


class IngestResponse(BaseModel):
    status: str
    filename: Optional[str] = None
    chunks: Optional[int] = None
    message: Optional[str] = None

class SelectDocsRequest(BaseModel):
    doc_ids: list[str]

class SelectDocsResponse(BaseModel):
    selected_docs: list[str]
