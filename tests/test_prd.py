"""Tests for PRD request validation, mocked Gemini generation, and response schema."""

import json
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.prd import PRDDocument, PRDGenerateRequest
from app.services.llm import GeminiLLMService, LLMServiceError, parse_prd_response
from tests.sample_prd import SAMPLE_PRD

VALID_IDEA = {
    "product_idea": "I want to build an app where college students can find tutors."
}


def test_valid_product_idea_returns_structured_prd(client, monkeypatch):
    mock_service = MagicMock()
    mock_service.generate_prd.return_value = PRDDocument.model_validate(SAMPLE_PRD)
    monkeypatch.setattr("app.api.routes.prd.get_llm_service", lambda: mock_service)

    response = client.post("/api/v1/prd/generate", json=VALID_IDEA)

    assert response.status_code == 200
    body = response.json()
    assert body["product_overview"]
    assert "personas" in body
    assert "user_stories" in body
    PRDDocument.model_validate(body)
    mock_service.generate_prd.assert_called_once()


def test_gemini_service_parses_mocked_model_json(monkeypatch):
    mock_response = MagicMock()
    mock_response.text = json.dumps(SAMPLE_PRD)

    mock_models = MagicMock()
    mock_models.generate_content.return_value = mock_response

    mock_client = MagicMock()
    mock_client.models = mock_models

    monkeypatch.setattr(
        "app.services.llm.settings",
        MagicMock(gemini_api_key="test-not-a-real-key", gemini_model="gemini-2.5-flash"),
    )
    monkeypatch.setattr("app.services.llm.genai.Client", lambda api_key: mock_client)

    document = GeminiLLMService().generate_prd(VALID_IDEA["product_idea"])

    assert document.product_overview
    PRDDocument.model_validate(document.model_dump())
    mock_models.generate_content.assert_called_once()
    _, kwargs = mock_models.generate_content.call_args
    assert kwargs["model"] == "gemini-2.5-flash"


def test_gemini_service_parses_fenced_json():
    fenced = "```json\n" + json.dumps(SAMPLE_PRD) + "\n```"
    document = parse_prd_response(fenced)
    assert document.personas[0].name == "Aisha"


def test_gemini_missing_api_key_returns_503(monkeypatch):
    monkeypatch.setattr(
        "app.services.llm.settings",
        MagicMock(gemini_api_key="", gemini_model="gemini-2.5-flash"),
    )
    with pytest.raises(LLMServiceError) as exc_info:
        GeminiLLMService().generate_prd("tutor app")
    assert exc_info.value.status_code == 503


def test_empty_product_idea_is_rejected(client):
    response = client.post("/api/v1/prd/generate", json={"product_idea": ""})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] is True
    assert payload["status_code"] == 422


def test_whitespace_only_product_idea_is_rejected(client):
    response = client.post("/api/v1/prd/generate", json={"product_idea": "   "})
    assert response.status_code == 422


def test_missing_product_idea_is_rejected(client):
    response = client.post("/api/v1/prd/generate", json={})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] is True
    assert payload["status_code"] == 422


def test_response_schema_accepts_complete_prd():
    document = PRDDocument.model_validate(SAMPLE_PRD)
    assert document.product_overview
    assert document.personas[0].name == "Aisha"
    assert document.user_stories[0].as_a == "student"


def test_response_schema_rejects_missing_section():
    incomplete = dict(SAMPLE_PRD)
    del incomplete["risks"]
    with pytest.raises(ValidationError):
        PRDDocument.model_validate(incomplete)


def test_request_schema_strips_whitespace():
    request = PRDGenerateRequest.model_validate(
        {"product_idea": "  Find tutors on campus  "}
    )
    assert request.product_idea == "Find tutors on campus"
