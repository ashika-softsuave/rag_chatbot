from backend.app.rag.embeddings import embed_query
from backend.app.rag.vector_store import collection

def retrieve_context(query: str, k: int = 5) -> str:
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        print("No matching chunks found")
        return ""

    context = "\n\n".join(documents)
    print("CONTEXT FOUND:\n", context[:500])
    return context
