"""API error-handling tests for PRD generation."""

from unittest.mock import MagicMock

import pytest

from app.services.llm import LLMServiceError


ENDPOINT = "/api/v1/prd/generate"
VALID_IDEA = {
    "product_idea": "I want to build an app where college students can find tutors."
}


def assert_error_response_shape(
    body: dict,
    *,
    status_code: int,
    message: str | None = None,
    has_details: bool | None = None,
) -> None:
    """Assert the existing application error response structure."""
    assert body["error"] is True
    assert body["status_code"] == status_code
    assert isinstance(body["message"], str)

    if message is not None:
        assert body["message"] == message

    if has_details is True:
        assert "details" in body
        assert isinstance(body["details"], list)
    elif has_details is False:
        assert "details" not in body


@pytest.mark.parametrize(
    ("payload", "expected_field_error"),
    [
        ({}, "missing"),
        ({"product_idea": ""}, "product_idea must not be empty"),
        ({"product_idea": "   "}, "product_idea must not be empty"),
    ],
)
def test_invalid_product_idea_requests_return_422(
    client,
    payload,
    expected_field_error,
):
    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422

    body = response.json()
    assert_error_response_shape(
        body,
        status_code=422,
        message="Request validation failed",
        has_details=True,
    )
    assert expected_field_error in response.text


def test_llm_service_failure_returns_intended_api_error(client, monkeypatch):
    mock_service = MagicMock()
    mock_service.generate_prd.side_effect = LLMServiceError(
        "The Gemini request failed. Please try again.",
        status_code=502,
    )

    monkeypatch.setattr(
        "app.api.routes.prd.get_llm_service",
        lambda: mock_service,
    )

    response = client.post(ENDPOINT, json=VALID_IDEA)

    assert response.status_code == 502

    assert_error_response_shape(
        response.json(),
        status_code=502,
        message="The Gemini request failed. Please try again.",
        has_details=False,
    )
    mock_service.generate_prd.assert_called_once_with(VALID_IDEA["product_idea"])


def test_llm_error_response_does_not_expose_api_keys(client, monkeypatch):
    secret_api_key = "test-secret-gemini-api-key"
    mock_service = MagicMock()
    mock_service.api_key = secret_api_key
    mock_service.generate_prd.side_effect = LLMServiceError(
        "Gemini authentication failed. Check that GEMINI_API_KEY is valid.",
        status_code=502,
    )

    monkeypatch.setattr(
        "app.api.routes.prd.get_llm_service",
        lambda: mock_service,
    )

    response = client.post(ENDPOINT, json=VALID_IDEA)

    assert response.status_code == 502
    assert_error_response_shape(
        response.json(),
        status_code=502,
        message="Gemini authentication failed. Check that GEMINI_API_KEY is valid.",
        has_details=False,
    )
    assert secret_api_key not in response.text
    assert "test-secret" not in response.text


def test_validation_error_response_follows_existing_error_structure(client):
    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422

    body = response.json()
    assert set(body) == {"error", "status_code", "message", "details"}
    assert_error_response_shape(
        body,
        status_code=422,
        message="Request validation failed",
        has_details=True,
    )


def test_llm_error_response_follows_existing_error_structure(client, monkeypatch):
    mock_service = MagicMock()
    mock_service.generate_prd.side_effect = LLMServiceError(
        "The Gemini request timed out. Please try again.",
        status_code=504,
    )

    monkeypatch.setattr(
        "app.api.routes.prd.get_llm_service",
        lambda: mock_service,
    )

    response = client.post(ENDPOINT, json=VALID_IDEA)

    assert response.status_code == 504
    body = response.json()
    assert set(body) == {"error", "status_code", "message"}
    assert_error_response_shape(
        body,
        status_code=504,
        message="The Gemini request timed out. Please try again.",
        has_details=False,
    )