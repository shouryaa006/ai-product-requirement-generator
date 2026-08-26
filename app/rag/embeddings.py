"""Embedding service utilizing the Google GenAI SDK."""

from typing import List

from google import genai

from app.core.config import settings


class EmbeddingServiceError(Exception):
    """Errors arising from embedding generation."""
    pass


class GeminiEmbeddingService:
    """Generates text embeddings using Google's GenAI SDK."""

    def __init__(self, api_key: str = "", model_name: str = "gemini-embedding-001"):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name

    def embed_text(self, text: str) -> List[float]:
        """Generates an embedding vector for a single text string."""
        if not self.api_key:
            raise EmbeddingServiceError("Gemini API key is missing. Set GEMINI_API_KEY in your .env file.")

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.embed_content(
                model=self.model_name,
                contents=text,
            )
            # Response contains `embedding` which has `values`
            if response.embeddings and response.embeddings[0].values:
                return response.embeddings[0].values
            raise EmbeddingServiceError("No embedding values returned in the response.")
        except Exception as exc:
            raise EmbeddingServiceError(f"Failed to generate embedding: {exc}") from exc

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of text strings."""
        if not self.api_key:
            raise EmbeddingServiceError("Gemini API key is missing. Set GEMINI_API_KEY in your .env file.")

        if not texts:
            return []

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.embed_content(
                model=self.model_name,
                contents=texts,
            )
            # Response may have embeddings for each element in the list
            if response.embeddings:
                return [emb.values for emb in response.embeddings]
            elif response.embedding:
                return [response.embedding.values]
            raise EmbeddingServiceError("No embeddings returned in the response.")
        except Exception as exc:
            raise EmbeddingServiceError(f"Failed to generate embeddings: {exc}") from exc


def get_embedding_service() -> GeminiEmbeddingService:
    """Factory function for embedding service."""
    return GeminiEmbeddingService()
