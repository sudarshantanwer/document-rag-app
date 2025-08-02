from app.db.session import async_session

async def select_documents(payload):
    # TODO: Mark docs for inclusion in RAG
    return {"selected_docs": payload.get("doc_ids", [])}
