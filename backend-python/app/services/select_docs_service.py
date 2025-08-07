from app.db.session import async_session

async def select_documents(payload):
    # Mark docs as selected for RAG (requires 'selected' field in Document model)
    doc_ids = payload.get("doc_ids", [])
    if not doc_ids:
        return {"error": "No doc_ids provided."}

    from app.db.models import Document
    import uuid

    updated = []
    async with async_session() as session:
        async with session.begin():
            for doc_id in doc_ids:
                try:
                    doc_uuid = uuid.UUID(doc_id)
                    doc = await session.get(Document, doc_uuid)
                    if doc:
                        # If 'selected' field exists, set it True. Otherwise, skip.
                        if hasattr(doc, 'selected'):
                            doc.selected = True
                            updated.append(str(doc.id))
                except Exception as e:
                    continue
    return {"selected_docs": updated}
