"""ChromaDB vector store manager."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb

from app.core.config import settings
from app.rag.chunking import DocumentChunk


class VectorStoreError(Exception):
    """Errors arising from vector database operations."""
    pass


class ChromaVectorStore:
    """Manages local, persistent storage of document chunks and embeddings in ChromaDB."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "prd_knowledge_base",
    ):
        # Configure persistence path
        self.persist_directory = persist_directory or os.getenv("RAG_PERSIST_DIRECTORY", "data/chroma")
        self.collection_name = collection_name

        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
        except Exception as exc:
            raise VectorStoreError(f"Failed to initialize ChromaDB client at '{self.persist_directory}': {exc}") from exc

    def upsert_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Upserts document chunks and their pre-computed embeddings into the store.

        Using stable IDs prevents uncontrolled duplicates if the command is run multiple times.
        """
        if not chunks:
            return

        if len(chunks) != len(embeddings):
            raise VectorStoreError("The number of chunks must match the number of pre-computed embeddings.")

        ids = [f"{chunk.source}_chunk_{chunk.chunk_index}" for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.to_metadata() for chunk in chunks]

        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        except Exception as exc:
            raise VectorStoreError(f"Failed to upsert chunks into ChromaDB: {exc}") from exc

    def query_similarity(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Queries the collection for similar documents using a query embedding."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            formatted_results = []
            if not results or "documents" not in results or not results["documents"][0]:
                return formatted_results

            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            ids = results["ids"][0]
            distances = results.get("distances", [[]])[0]

            for idx in range(len(documents)):
                formatted_results.append({
                    "id": ids[idx],
                    "text": documents[idx],
                    "metadata": metadatas[idx] if metadatas else {},
                    "distance": distances[idx] if distances else None,
                })

            return formatted_results
        except Exception as exc:
            raise VectorStoreError(f"Failed to query ChromaDB: {exc}") from exc

    def count(self) -> int:
        """Returns the total number of items stored in the collection."""
        try:
            return self.collection.count()
        except Exception as exc:
            raise VectorStoreError(f"Failed to get collection count: {exc}") from exc

    def delete_by_source(self, source_filename: str) -> None:
        """Deletes all items associated with a specific source filename."""
        try:
            self.collection.delete(where={"source": source_filename})
        except Exception as exc:
            raise VectorStoreError(f"Failed to delete items by source '{source_filename}': {exc}") from exc


def get_vector_store() -> ChromaVectorStore:
    """Factory function to get vector store instance using current settings."""
    persist_dir = os.getenv("RAG_PERSIST_DIRECTORY", "data/chroma")
    return ChromaVectorStore(persist_directory=persist_dir)
