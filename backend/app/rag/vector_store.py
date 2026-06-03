"""
Vector Store — Store and search document embeddings.
Uses ChromaDB with built-in local embeddings (no API needed).
"""
import chromadb
from typing import List, Dict
from app.rag.config import VECTOR_STORE_DIR, TOP_K, SIMILARITY_THRESHOLD

# Collection name
COLLECTION_NAME = "frs_knowledge_base"


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create a persistent ChromaDB client."""
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    return client


def get_or_create_collection(client: chromadb.ClientAPI = None):
    """Get or create the FRS knowledge base collection."""
    if client is None:
        client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "FRS IT Development Company Knowledge Base"},
    )
    return collection


def add_documents(chunks: List[Dict], collection=None):
    """
    Add chunked documents to the vector store.
    ChromaDB generates embeddings automatically using its default model.
    """
    if collection is None:
        collection = get_or_create_collection()

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {"source": chunk["source"], "chunk_index": chunk["chunk_index"]}
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )
    return len(ids)


def search(query: str, top_k: int = TOP_K, collection=None) -> List[Dict]:
    """
    Search for the most relevant chunks given a query.
    ChromaDB handles embedding the query automatically.
    """
    if collection is None:
        collection = get_or_create_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    formatted = []
    if results and results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if results["distances"] else 1.0
            similarity = 1.0 / (1.0 + distance)
            if similarity >= SIMILARITY_THRESHOLD:
                formatted.append({
                    "text": doc,
                    "source": results["metadatas"][0][i].get("source", "unknown"),
                    "chunk_index": results["metadatas"][0][i].get("chunk_index", 0),
                    "similarity": round(similarity, 4),
                })

    return formatted


def clear_collection():
    """Delete and recreate the collection (for re-indexing)."""
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return get_or_create_collection(client)


def get_collection_stats() -> Dict:
    """Get statistics about the vector store."""
    collection = get_or_create_collection()
    return {
        "name": COLLECTION_NAME,
        "total_chunks": collection.count(),
    }
