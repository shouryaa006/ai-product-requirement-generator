"""Integration and flow tests for the backend PRD generation."""

import json
from unittest.mock import MagicMock
import pytest
from app.schemas.prd import PRDDocument
from tests.sample_prd import SAMPLE_PRD


def test_backend_prd_generation_flow_successful(client, monkeypatch):
    """
    Test POST /api/v1/prd/generate to verify the full backend flow.
    We mock the external API/LLM calls and the RAG components to ensure the test
    runs locally without any real network connections or active API keys.
    """
    # 1. Setup the mock response from Gemini LLM
    mock_response = MagicMock()
    mock_response.text = json.dumps(SAMPLE_PRD)

    mock_models = MagicMock()
    mock_models.generate_content.return_value = mock_response

    mock_genai_client = MagicMock()
    mock_genai_client.models = mock_models

    monkeypatch.setattr(
        "app.services.llm.genai.Client",
        lambda api_key: mock_genai_client,
    )

    # 2. Patch the settings to include a dummy API key to pass verification
    monkeypatch.setattr(
        "app.services.llm.settings",
        MagicMock(
            gemini_api_key="mock-api-key-for-flow-test",
            gemini_model="gemini-2.5-flash",
        ),
    )

    # 3. Setup the mock retriever for the RAG component
    mock_retriever = MagicMock()
    mock_retriever.vector_store.count.return_value = 4
    mock_retriever.retrieve_relevant_knowledge.return_value = [
        {
            "id": "chunk_1",
            "text": "Tutor marketplace for college students.",
            "metadata": {"title": "Knowledge Document", "source": "knowledge.md"},
            "distance": 0.05,
        }
    ]

    monkeypatch.setattr(
        "app.rag.retriever.get_retrieval_service",
        lambda: mock_retriever,
    )

    # 4. Mock the multi-agent compiled graph invoke to verify it is NOT called
    # (since the current API endpoint utilizes the single-agent GeminiLLMService)
    mock_graph_invoke = MagicMock()
    monkeypatch.setattr(
        "app.agents.graph.compiled_graph.invoke",
        mock_graph_invoke,
    )

    # 5. Call the API endpoint
    payload = {
        "product_idea": "I want to build an app where college students can find tutors."
    }
    response = client.post("/api/v1/prd/generate", json=payload)

    # 6. Verify HTTP 200
    assert response.status_code == 200

    # 7. Validate the response against PRDDocument
    body = response.json()
    prd_doc = PRDDocument.model_validate(body)

    # 8. Verify important PRD sections are present
    assert prd_doc.product_overview is not None
    assert prd_doc.problem_statement is not None
    assert len(prd_doc.target_users) > 0
    assert len(prd_doc.personas) > 0
    assert len(prd_doc.business_objectives) > 0
    assert len(prd_doc.user_stories) > 0
    assert len(prd_doc.functional_requirements) > 0
    assert len(prd_doc.non_functional_requirements) > 0

    # 9. Verify the current API does NOT invoke the multi-agent workflow,
    # reflecting that the route is built on the single-agent GeminiLLMService.
    mock_graph_invoke.assert_not_called()
