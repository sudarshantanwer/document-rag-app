from app.db.session import async_session
from app.services.cache_service import cache_service
from app.utils.cached_embeddings import create_cached_embeddings
# from langchain.vectorstores.pgvector import PGVector
# from langchain.llms import OpenAI, HuggingFaceLLM

async def query_documents(payload):
    from langchain_community.vectorstores.pgvector import PGVector
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.llms import HuggingFacePipeline
    from transformers import pipeline
    import os

    question = payload.get("question", "")
    if not question:
        return {"error": "No question provided."}

    doc_id = payload.get("doc_id")
    k = payload.get("k", 10)

    # Check cache for complete query result first
    cached_result = await cache_service.get_query_cache(question, doc_id, k)
    if cached_result:
        return cached_result

    # Load embeddings with caching wrapper
    base_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embeddings = create_cached_embeddings(base_embeddings, "sentence-transformers/all-MiniLM-L6-v2")
    
    pgvector_conn = os.getenv("PGVECTOR_CONN")
    if not pgvector_conn:
        return {"error": "PGVECTOR_CONN environment variable not set."}
    
    vectorstore = PGVector(
        connection_string=pgvector_conn,
        embedding_function=embeddings,
        collection_name="documents"
    )

    # Check cache for similarity search results
    cached_docs = await cache_service.get_similarity_search_cache(question, doc_id, k)
    if cached_docs:
        # Reconstruct document objects from cached data
        from types import SimpleNamespace
        docs = [SimpleNamespace(page_content=doc['page_content'], metadata=doc['metadata']) for doc in cached_docs]
    else:
        # Perform similarity search
        filter_kwargs = {}
        if doc_id:
            filter_kwargs = {"metadata": {"document_id": doc_id}}
        
        docs = vectorstore.similarity_search(question, k=k, **filter_kwargs)
        
        # Cache the similarity search results
        await cache_service.set_similarity_search_cache(question, docs, doc_id, k)

    context = "\n".join([doc.page_content for doc in docs])

    # Truncate context to fit model's max token limit (approx 200 words)
    max_words = 200
    context_words = context.split()
    if len(context_words) > max_words:
        context = " ".join(context_words[:max_words])

    # Generate answer using HuggingFacePipeline
    qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")
    llm = HuggingFacePipeline(pipeline=qa_pipeline)
    prompt = (
        "Answer the question based only on the context below. "
        # "If unsure, say 'I don't know.'\n\n"
        f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    )
    answer = llm(prompt)
    
    result = {"answer": answer, "context": context}
    
    # Cache the complete result
    await cache_service.set_query_cache(question, result, doc_id, k)
    
    return result
