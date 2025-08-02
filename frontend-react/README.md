# Document-RAG React Frontend

This is a simple React app (Vite) to interact with a FastAPI Document-RAG backend.

## Features
- Upload documents (PDF/txt/docx) for ingestion
- Query documents using RAG (LLM-powered answers)
- Select specific documents for RAG

## Endpoints Consumed
- `POST /ingest` — Upload and embed documents
- `POST /query` — Ask questions, get answers
- `POST /select-docs` — Specify docs for RAG

## Getting Started
1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Ensure FastAPI backend is running and accessible

## Configuration
- Update API base URL in the frontend as needed to match your backend
