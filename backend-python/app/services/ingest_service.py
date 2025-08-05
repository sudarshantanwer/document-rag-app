from app.db.models import Document
from app.db.session import async_session
# from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
# from langchain.text_splitter import TextSplitter
# from langchain.vectorstores.pgvector import PGVector

import os
from tempfile import NamedTemporaryFile
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document
from app.db.session import async_session

async def ingest_document(file):
    # Save uploaded file to temp location
    suffix = os.path.splitext(file.filename)[1]
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Parse file content
    if suffix == ".txt":
        with open(tmp_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif suffix == ".pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(tmp_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix == ".docx":
        from docx import Document as DocxDocument
        doc = DocxDocument(tmp_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        os.remove(tmp_path)
        return {"status": "error", "message": "Unsupported file type"}

    # Generate embeddings (choose model)
    # embeddings = OpenAIEmbeddings()  # or HuggingFaceEmbeddings()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Split text
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_text(text)

    # Store in pgvector via Langchain
    vectorstore = PGVector(
        connection_string=os.getenv("PGVECTOR_CONN", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"),
        embedding_function=embeddings,
        collection_name="documents"
    )
    ids = vectorstore.add_texts(docs)

    # Store metadata in DB
    async with async_session() as session:
        async with session.begin():
            doc = Document(filename=file.filename, num_chunks=len(docs), vector_ids=ids)
            session.add(doc)

    os.remove(tmp_path)
    return {"status": "success", "filename": file.filename, "chunks": len(docs)}
