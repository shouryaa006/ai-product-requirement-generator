"""Gemini-backed LLM service. Routes should call this, not the Gemini SDK."""

import json
import re

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.prd import PRDDocument
from app.services.prompts import SYSTEM_PROMPT, build_user_prompt

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


class LLMServiceError(Exception):
    """Safe, user-facing failure from the LLM layer."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _extract_json_text(raw: str) -> str:
    """Strip optional Markdown code fences so json.loads can parse the body."""
    return _FENCE_RE.sub("", raw.strip()).strip()


def parse_prd_response(raw_content: str) -> PRDDocument:
    """Turn model text into a validated PRDDocument."""
    if not raw_content or not raw_content.strip():
        raise LLMServiceError("The model returned an empty response.", status_code=502)

    try:
        payload = json.loads(_extract_json_text(raw_content))
    except json.JSONDecodeError:
        raise LLMServiceError("The model returned invalid JSON.", status_code=502) from None

    try:
        return PRDDocument.model_validate(payload)
    except ValidationError:
        raise LLMServiceError(
            "The model response did not match the required PRD schema.",
            status_code=502,
        ) from None


def _status_code_from_gemini(exc: Exception) -> int | None:
    for attr in ("code", "status_code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    return None


class GeminiLLMService:
    """Talks to Gemini and returns a validated PRDDocument."""

    def generate_prd(self, product_idea: str) -> PRDDocument:
        if not settings.gemini_api_key:
            raise LLMServiceError(
                "Gemini is not configured. Set GEMINI_API_KEY in your .env file.",
                status_code=503,
            )

        # 1. RAG Retrieval Step (Step 8)
        retrieved_context = ""
        try:
            from app.rag.retriever import get_retrieval_service
            from app.rag.vector_store import VectorStoreError
            from app.rag.embeddings import EmbeddingServiceError
            from app.rag.retriever import RetrievalServiceError
            
            retriever = get_retrieval_service()
            
            # Verify database count to handle empty knowledge base or unavailable DB (Step 13)
            try:
                count = retriever.vector_store.count()
                if count == 0:
                    raise LLMServiceError(
                        "The product knowledge base is empty. Please run ingestion first.",
                        status_code=503,
                    )
            except Exception as e:
                if isinstance(e, LLMServiceError):
                    raise
                raise LLMServiceError(
                    f"Vector database is unavailable or not initialized: {e}",
                    status_code=503,
                ) from None

            # Retrieve relevant chunks
            results = retriever.retrieve_relevant_knowledge(product_idea)
            
            # Log/display RAG debug information (Step 15)
            print(f"\n--- RAG DEBUG INFORMATION ---")
            print(f"Query: '{product_idea}'")
            print(f"Retrieved: {len(results)} chunks")
            for idx, res in enumerate(results):
                src = res.get("metadata", {}).get("source", "unknown")
                dist = res.get("distance")
                print(f"  Chunk {idx + 1}: Source File: '{src}', Distance Score: {dist}")
            print(f"-----------------------------\n")

            if results:
                # Format retrieved context for grounded prompt
                context_parts = []
                for res in results:
                    src_title = res.get("metadata", {}).get("title", "Reference Document")
                    src_file = res.get("metadata", {}).get("source", "unknown")
                    context_parts.append(
                        f"From Document '{src_title}' (Source: {src_file}):\n{res['text']}"
                    )
                retrieved_context = "\n\n---\n\n".join(context_parts)
                
        except LLMServiceError:
            raise
        except (VectorStoreError, EmbeddingServiceError, RetrievalServiceError) as exc:
            print(f"RAG components raised a known error: {exc}")
            raise LLMServiceError(
                f"RAG system failed: {exc}",
                status_code=502,
            ) from None
        except Exception as exc:
            print(f"Unexpected RAG Retrieval failure: {exc}")
            raise LLMServiceError(
                "Failed to retrieve relevant product knowledge for RAG.",
                status_code=502,
            ) from None

        client = genai.Client(api_key=settings.gemini_api_key)

        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=build_user_prompt(product_idea, retrieved_context),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                    response_mime_type="application/json",
                    response_schema=PRDDocument,
                ),
            )
        except genai_errors.ClientError as exc:
            status = _status_code_from_gemini(exc)
            print(f"Gemini client error: {type(exc).__name__}")
            if status in {401, 403}:
                raise LLMServiceError(
                    "Gemini authentication failed. Check that GEMINI_API_KEY is valid.",
                    status_code=502,
                ) from None
            if status == 429:
                raise LLMServiceError(
                    "Gemini rate limit reached. Please try again later.",
                    status_code=429,
                ) from None
            raise LLMServiceError(
                "The Gemini request failed. Please try again.",
                status_code=502,
            ) from None
        except genai_errors.ServerError:
            print("Gemini server error")
            raise LLMServiceError(
                "The Gemini request failed. Please try again.",
                status_code=502,
            ) from None
        except TimeoutError:
            raise LLMServiceError(
                "The Gemini request timed out. Please try again.",
                status_code=504,
            ) from None
        except LLMServiceError:
            raise
        except Exception as exc:
            print(f"Unexpected LLM error: {type(exc).__name__}")
            raise LLMServiceError(
                "PRD generation failed. Please try again.",
                status_code=502,
            ) from None

        raw_content = getattr(response, "text", None) or ""
        return parse_prd_response(raw_content)


def get_llm_service() -> GeminiLLMService:
    """Factory so tests can replace the service without changing the route."""
    return GeminiLLMService()
