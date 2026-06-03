"""
Embeddings Generator — Uses ChromaDB default embeddings (local, free).
No external API needed.
"""
from typing import List


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings using ChromaDB's default embedding function.
    Uses all-MiniLM-L6-v2 via onnxruntime — runs locally, no API needed.
    """
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    ef = DefaultEmbeddingFunction()
    return ef(texts)


def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for a search query."""
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    ef = DefaultEmbeddingFunction()
    result = ef([query])
    return result[0]
