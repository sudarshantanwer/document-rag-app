<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a React app created with Vite. The backend is a FastAPI Document-RAG system with endpoints:
- POST /ingest: upload PDF/txt/docx, generate embeddings, store in pgvector
- POST /query: user question, similarity search, LLM answer
- POST /select-docs: specify docs for RAG

Generate React components and API calls to interact with these endpoints.
