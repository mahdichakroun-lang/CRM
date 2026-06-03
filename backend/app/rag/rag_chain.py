"""
RAG Chain — Full Retrieval-Augmented Generation pipeline.
Orchestrates: Query → Retrieve → Generate.
"""
import logging
from typing import Dict, List, Optional
from app.rag.vector_store import search, get_collection_stats
from app.rag.llm_client import generate_answer

logger = logging.getLogger("rag")


def ask(query: str, top_k: int = 5) -> Dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from vector store
    2. Generate answer using LLM with context
    3. Return answer + sources

    Returns:
        {
            "answer": str,
            "sources": [{"source": str, "similarity": float}],
            "chunks_used": int,
        }
    """
    logger.info(f"RAG query: {query[:100]}...")

    # Step 1: Retrieve relevant chunks
    retrieved_chunks = search(query, top_k=top_k)
    logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")

    # Step 2: Generate answer with LLM
    answer = generate_answer(query, retrieved_chunks)

    # Step 3: Collect unique sources
    sources = []
    seen_sources = set()
    for chunk in retrieved_chunks:
        if chunk["source"] not in seen_sources:
            sources.append({
                "source": chunk["source"],
                "similarity": chunk["similarity"],
            })
            seen_sources.add(chunk["source"])

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(retrieved_chunks),
    }


def get_status() -> Dict:
    """Get the current status of the RAG system."""
    try:
        stats = get_collection_stats()
        return {
            "status": "ready" if stats["total_chunks"] > 0 else "empty",
            "total_chunks": stats["total_chunks"],
            "collection": stats["name"],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
