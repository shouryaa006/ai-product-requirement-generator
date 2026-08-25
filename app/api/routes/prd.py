"""PRD generation endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.prd import PRDDocument, PRDGenerateRequest
from app.services.llm import LLMServiceError, get_llm_service

router = APIRouter(prefix="/api/v1/prd", tags=["prd"])


@router.post("/generate", response_model=PRDDocument)
def generate_prd(payload: PRDGenerateRequest) -> PRDDocument:
    """Turn a product idea into a structured PRD using Gemini."""
    service = get_llm_service()
    try:
        return service.generate_prd(payload.product_idea)
    except LLMServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None
