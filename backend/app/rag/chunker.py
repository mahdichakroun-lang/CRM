"""
Document Chunker — Split documents into smaller overlapping chunks.
Step 1 of the RAG pipeline.
"""
import re
from pathlib import Path
from typing import List, Dict
from app.rag.config import RAG_DOCUMENTS_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def load_documents(directory: Path = RAG_DOCUMENTS_DIR) -> List[Dict]:
    """Load all markdown documents from the RAG documents directory."""
    documents = []
    if not directory.exists():
        raise FileNotFoundError(f"RAG documents directory not found: {directory}")

    for filepath in sorted(directory.glob("*.md")):
        content = filepath.read_text(encoding="utf-8")
        documents.append({
            "filename": filepath.name,
            "content": content,
            "source": filepath.stem,
        })
    return documents


def clean_text(text: str) -> str:
    """Clean markdown text for better chunking."""
    # Remove markdown formatting but keep structure
    text = re.sub(r"#{1,6}\s*", "", text)        # Remove # headers
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)  # Remove bold/italic
    text = re.sub(r"`([^`]+)`", r"\1", text)     # Remove inline code
    text = re.sub(r"```[\s\S]*?```", "", text)   # Remove code blocks
    text = re.sub(r"\|[^\n]+\|", "", text)       # Remove table rows (simplified)
    text = re.sub(r"---+", "", text)             # Remove horizontal rules
    text = re.sub(r"\n{3,}", "\n\n", text)       # Reduce multiple newlines
    return text.strip()


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into overlapping chunks by sentences.
    Uses sentence boundaries instead of character cuts for cleaner chunks.
    """
    # Split by sentence endings
    sentences = re.split(r"(?<=[.!?])\s+|\n\n+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence exceeds chunk_size, save current and start new
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap: take the last part of the current chunk
            overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
            current_chunk = overlap_text + " " + sentence
        else:
            current_chunk = (current_chunk + " " + sentence).strip()

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunk_all_documents() -> List[Dict]:
    """
    Load all documents, clean them, and split into chunks.
    Returns a list of dicts with: text, source, chunk_index.
    """
    documents = load_documents()
    all_chunks = []

    for doc in documents:
        cleaned = clean_text(doc["content"])
        chunks = split_into_chunks(cleaned)
        for i, chunk_text in enumerate(chunks):
            if len(chunk_text) < 20:  # Skip tiny chunks
                continue
            all_chunks.append({
                "id": f"{doc['source']}_chunk_{i}",
                "text": chunk_text,
                "source": doc["filename"],
                "chunk_index": i,
            })

    return all_chunks


if __name__ == "__main__":
    # Quick test
    chunks = chunk_all_documents()
    print(f"Total chunks: {len(chunks)}")
    for c in chunks[:3]:
        print(f"\n--- {c['id']} ({len(c['text'])} chars) ---")
        print(c["text"][:200] + "...")
