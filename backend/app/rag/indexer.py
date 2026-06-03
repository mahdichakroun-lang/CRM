"""
Document Indexer — Index all RAG documents into the vector store.
Uses ChromaDB's built-in embeddings (no external API needed).

Usage:
    python -m app.rag.indexer
"""
import logging
import sys
from app.rag.chunker import chunk_all_documents
from app.rag.vector_store import clear_collection, add_documents, get_collection_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("indexer")


def index_documents(force: bool = False):
    """
    Full indexing pipeline:
    1. Load & chunk all documents
    2. Store in ChromaDB (embeddings generated automatically)
    """
    logger.info("🚀 Starting RAG document indexing...")

    # Step 1: Chunk documents
    logger.info("📄 Step 1/2 — Loading and chunking documents...")
    chunks = chunk_all_documents()
    logger.info(f"   ✅ Created {len(chunks)} chunks from documents")

    if not chunks:
        logger.error("   ❌ No chunks created. Check rag_documents/ directory.")
        return

    # Show chunk distribution
    sources = {}
    for c in chunks:
        sources[c["source"]] = sources.get(c["source"], 0) + 1
    for src, count in sources.items():
        logger.info(f"   📑 {src}: {count} chunks")

    # Step 2: Store in vector database (ChromaDB generates embeddings internally)
    logger.info("💾 Step 2/2 — Storing in ChromaDB (with auto-embeddings)...")
    if force:
        logger.info("   🗑️  Clearing existing collection (force=True)...")
        clear_collection()

    count = add_documents(chunks)
    logger.info(f"   ✅ Stored {count} chunks in vector store")

    # Final stats
    stats = get_collection_stats()
    logger.info(f"")
    logger.info(f"🎉 Indexing complete!")
    logger.info(f"   Collection: {stats['name']}")
    logger.info(f"   Total chunks: {stats['total_chunks']}")


if __name__ == "__main__":
    force = "--force" in sys.argv
    index_documents(force=force)
