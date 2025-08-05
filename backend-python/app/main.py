
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.select_docs import router as select_docs_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(select_docs_router)
