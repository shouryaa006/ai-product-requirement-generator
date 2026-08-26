"""Retrieval service for RAG system."""

import os
from typing import Any, Dict, List, Optional

from app.rag.embeddings import get_embedding_service
from app.rag.vector_store import get_vector_store


class RetrievalServiceError(Exception):
    """Errors arising from retrieval operations."""
    pass


class RetrievalService:
    """Orchestrates similarity search of document chunks using embeddings."""

    def __init__(
        self,
        embedding_service=None,
        vector_store=None,
        default_top_k: int = 5,
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or get_vector_store()

        # Load configurable default_top_k from env if present
        env_top_k = os.getenv("RAG_TOP_K", "").strip()
        self.default_top_k = int(env_top_k) if env_top_k.isdigit() else default_top_k

    def retrieve_relevant_knowledge(
        self,
        product_idea: str,
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Finds and returns the most relevant knowledge chunks for a given product idea."""
        if not product_idea or not product_idea.strip():
            return []

        k = top_k if top_k is not None else self.default_top_k

        try:
            # 1. Convert the product idea into an embedding
            query_embedding = self.embedding_service.embed_text(product_idea)

            # 2. Search the vector database
            raw_results = self.vector_store.query_similarity(query_embedding, top_k=k)

            # 3. Format and return results
            # Expected raw_results format: List of dicts with keys: id, text, metadata, distance
            return raw_results
        except Exception as exc:
            raise RetrievalServiceError(f"RAG retrieval failed: {exc}") from exc


def get_retrieval_service() -> RetrievalService:
    """Factory function for RetrievalService."""
    return RetrievalService()
