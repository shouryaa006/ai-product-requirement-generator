"""Ingestion script to build or update the local vector store from Markdown documents."""

import sys
from pathlib import Path

from app.core.config import PROJECT_ROOT, settings
from app.rag.chunking import chunk_all_documents
from app.rag.documents import load_knowledge_documents
from app.rag.embeddings import get_embedding_service
from app.rag.vector_store import get_vector_store


def run_ingestion(knowledge_dir: Path) -> None:
    """Orchestrates loading, chunking, embedding, and storing markdown documents."""
    print(f"Starting knowledge base ingestion from: {knowledge_dir}")

    # 1. Validation and Configuration Checks
    if not settings.gemini_api_key:
        print("Error: GEMINI_API_KEY is not set in the environment or .env file.", file=sys.stderr)
        sys.exit(1)

    if not knowledge_dir.exists():
        print(f"Error: Knowledge directory '{knowledge_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # 2. Load Documents
    try:
        documents = load_knowledge_documents(knowledge_dir)
    except Exception as exc:
        print(f"Error: Failed to load documents: {exc}", file=sys.stderr)
        sys.exit(1)

    if not documents:
        print(f"Warning: No Markdown documents found in '{knowledge_dir}'. Empty knowledge base initialized.")
        return

    print(f"Loaded {len(documents)} documents successfully.")

    # 3. Chunk Documents
    chunks = chunk_all_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    # 4. Generate Embeddings
    print("Generating embeddings via Gemini API...")
    embedding_service = get_embedding_service()
    try:
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)
    except Exception as exc:
        print(f"Error: Embedding generation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # 5. Store in Local Vector DB
    print("Storing chunks and embeddings in persistent ChromaDB store...")
    try:
        vector_store = get_vector_store()
        vector_store.upsert_chunks(chunks, embeddings)
        print(f"Successfully indexed/updated {len(chunks)} chunks from {len(documents)} documents.")
        print(f"Total items in vector database: {vector_store.count()}")
    except Exception as exc:
        print(f"Error: Vector store operation failed: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Command-line entry point."""
    default_knowledge_dir = PROJECT_ROOT / "knowledge"
    run_ingestion(default_knowledge_dir)


if __name__ == "__main__":
    main()
