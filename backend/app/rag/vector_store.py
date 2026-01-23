import chromadb
from chromadb.config import Settings

# Persistent client
client = chromadb.Client(
    Settings(
        persist_directory="chroma_db",
        is_persistent=True,
        anonymized_telemetry=False
    )
)

COLLECTION_NAME = "rag_docs"

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


def add_chunks(texts, embeddings, metadatas):
    if not texts or not embeddings:
        print(" Nothing to add to ChromaDB")
        return

    ids = [f"chunk_{collection.count() + i}" for i in range(len(texts))]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(" Added chunks:", len(texts))
    print(" TOTAL CHUNKS IN DB:", collection.count())

def query_chunks(query_embedding, k=6):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

def debug_count():
    print(" TOTAL CHUNKS IN DB:", collection.count())
