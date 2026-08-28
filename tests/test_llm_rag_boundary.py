"""Deterministic tests for the LLM service RAG integration boundary."""

import json
from unittest.mock import MagicMock

import pytest

from app.rag.retriever import RetrievalServiceError
from app.rag.vector_store import VectorStoreError
from app.services.llm import GeminiLLMService, LLMServiceError
from tests.sample_prd import SAMPLE_PRD


def patch_llm_settings(monkeypatch):
    monkeypatch.setattr(
        "app.services.llm.settings",
        MagicMock(
            gemini_api_key="test-not-a-real-key",
            gemini_model="gemini-2.5-flash",
        ),
    )


def patch_genai_client(monkeypatch):
    response = MagicMock()
    response.text = json.dumps(SAMPLE_PRD)

    models = MagicMock()
    models.generate_content.return_value = response

    client = MagicMock()
    client.models = models

    monkeypatch.setattr(
        "app.services.llm.genai.Client",
        lambda api_key: client,
    )
    return client


def test_llm_service_injects_retrieved_rag_context_into_prompt(monkeypatch):
    patch_llm_settings(monkeypatch)
    client = patch_genai_client(monkeypatch)

    retriever = MagicMock()
    retriever.vector_store.count.return_value = 2
    retriever.retrieve_relevant_knowledge.return_value = [
        {
            "text": "Validate tutor discovery with student interviews.",
            "metadata": {
                "title": "Product Discovery",
                "source": "product_discovery.md",
            },
            "distance": 0.05,
        },
        {
            "text": "Search results should prioritize verified tutor profiles.",
            "metadata": {
                "title": "Functional Requirements",
                "source": "functional_requirements.md",
            },
            "distance": 0.11,
        },
    ]
    monkeypatch.setattr(
        "app.rag.retriever.get_retrieval_service",
        lambda: retriever,
    )

    product_idea = "An app where college students can find tutors."
    document = GeminiLLMService().generate_prd(product_idea)

    assert document.product_overview == SAMPLE_PRD["product_overview"]
    retriever.vector_store.count.assert_called_once_with()
    retriever.retrieve_relevant_knowledge.assert_called_once_with(product_idea)

    client.models.generate_content.assert_called_once()
    call_kwargs = client.models.generate_content.call_args.kwargs
    prompt = call_kwargs["contents"]

    assert product_idea in prompt
    assert "RETRIEVED PRODUCT KNOWLEDGE" in prompt
    assert (
        "From Document 'Product Discovery' (Source: product_discovery.md):\n"
        "Validate tutor discovery with student interviews."
    ) in prompt
    assert "---" in prompt
    assert (
        "From Document 'Functional Requirements' "
        "(Source: functional_requirements.md):\n"
        "Search results should prioritize verified tutor profiles."
    ) in prompt


def test_llm_service_rejects_empty_knowledge_base_before_gemini_call(monkeypatch):
    patch_llm_settings(monkeypatch)
    client = patch_genai_client(monkeypatch)

    retriever = MagicMock()
    retriever.vector_store.count.return_value = 0
    monkeypatch.setattr(
        "app.rag.retriever.get_retrieval_service",
        lambda: retriever,
    )

    with pytest.raises(LLMServiceError) as exc_info:
        GeminiLLMService().generate_prd("Tutor marketplace")

    assert exc_info.value.status_code == 503
    assert exc_info.value.message == (
        "The product knowledge base is empty. Please run ingestion first."
    )
    retriever.retrieve_relevant_knowledge.assert_not_called()
    client.models.generate_content.assert_not_called()


def test_llm_service_maps_vector_count_failure_to_safe_error(monkeypatch):
    patch_llm_settings(monkeypatch)
    client = patch_genai_client(monkeypatch)

    retriever = MagicMock()
    retriever.vector_store.count.side_effect = VectorStoreError("Chroma unavailable")
    monkeypatch.setattr(
        "app.rag.retriever.get_retrieval_service",
        lambda: retriever,
    )

    with pytest.raises(LLMServiceError) as exc_info:
        GeminiLLMService().generate_prd("Tutor marketplace")

    assert exc_info.value.status_code == 503
    assert exc_info.value.message == (
        "Vector database is unavailable or not initialized: Chroma unavailable"
    )
    retriever.retrieve_relevant_knowledge.assert_not_called()
    client.models.generate_content.assert_not_called()


def test_llm_service_maps_retrieval_failure_to_safe_error(monkeypatch):
    patch_llm_settings(monkeypatch)
    client = patch_genai_client(monkeypatch)

    retriever = MagicMock()
    retriever.vector_store.count.return_value = 3
    retriever.retrieve_relevant_knowledge.side_effect = RetrievalServiceError(
        "Embedding generation failed"
    )
    monkeypatch.setattr(
        "app.rag.retriever.get_retrieval_service",
        lambda: retriever,
    )

    with pytest.raises(LLMServiceError) as exc_info:
        GeminiLLMService().generate_prd("Tutor marketplace")

    assert exc_info.value.status_code == 502
    assert exc_info.value.message == "RAG system failed: Embedding generation failed"
    client.models.generate_content.assert_not_called()