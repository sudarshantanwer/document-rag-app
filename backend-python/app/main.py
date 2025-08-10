
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.select_docs import router as select_docs_router
from app.routes.documents import router as documents_router
from app.db.models import Base
from app.db.session import engine

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Docker frontend
        "http://frontend:3000"    # Docker internal network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables initialized!")

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(select_docs_router)
app.include_router(documents_router)
