from app.db.models import Document
from app.db.session import async_session
# from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
# from langchain.text_splitter import TextSplitter
# from langchain.vectorstores.pgvector import PGVector

async def ingest_document(file):
    # TODO: Parse file, generate embeddings, store in DB
    return {"status": "success", "filename": file.filename}
