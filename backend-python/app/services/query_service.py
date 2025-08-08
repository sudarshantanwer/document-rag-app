from app.db.session import async_session
# from langchain.vectorstores.pgvector import PGVector
# from langchain.llms import OpenAI, HuggingFaceLLM

async def query_documents(payload):
    from langchain.vectorstores.pgvector import PGVector
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.llms import HuggingFacePipeline
    from transformers import pipeline
    import os

    question = payload.get("question", "")
    if not question:
        return {"error": "No question provided."}

    # Load embeddings and vectorstore
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    pgvector_conn = os.getenv("PGVECTOR_CONN")
    if not pgvector_conn:
        return {"error": "PGVECTOR_CONN environment variable not set."}
    vectorstore = PGVector(
        connection_string=pgvector_conn,
        embedding_function=embeddings,
        collection_name="documents"
    )

    # Restrict search to selected document if doc_id is provided
    doc_id = payload.get("doc_id")
    filter_kwargs = {}
    if doc_id:
        # PGVector filter expects metadata, so we filter by document id in metadata
        filter_kwargs = {"metadata": {"document_id": doc_id}}
    docs = vectorstore.similarity_search(question, k=10, **filter_kwargs)
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
    return {"answer": answer, "context": context}
