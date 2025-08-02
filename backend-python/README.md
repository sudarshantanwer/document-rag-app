# FastAPI Document-RAG Backend

This backend provides endpoints for document ingestion, querying with RAG, and document selection. It uses FastAPI, async SQLAlchemy, Langchain/LlamaIndex, pgvector, and python-dotenv.

## Features
- **POST /ingest**: Upload PDF/txt/docx, generate embeddings, store in PostgreSQL+pgvector
- **POST /query**: Ask questions, retrieve relevant docs, get LLM answer using RAG
- **POST /select-docs**: Specify docs for RAG process

## Tech Stack
- FastAPI
- async SQLAlchemy
- Langchain or LlamaIndex
- pgvector
- python-dotenv

## Running Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Start server: `uvicorn app.main:app --reload`
3. Configure environment variables in `.env`
