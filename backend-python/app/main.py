from fastapi import FastAPI
from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.select_docs import router as select_docs_router

app = FastAPI()

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(select_docs_router)
