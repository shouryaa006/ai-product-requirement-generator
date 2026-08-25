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

        client = genai.Client(api_key=settings.gemini_api_key)

        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=build_user_prompt(product_idea),
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
